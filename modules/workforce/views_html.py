from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from kernel.exceptions import PermissionDeniedException
from modules.workforce.services.device_service import DeviceRegistrationService
from modules.workforce.services.query_service import WorkforceAttendanceQueryService
from kernel.models import Person # Needed to fetch staff names for display if not included in summary dict

def get_campus_context(request):
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return None
    return int(campus_id)

def _get_person_id(request):
    person = getattr(request.user, 'person', None)
    return str(person.id) if person else None

@login_required
def workforce_dashboard(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(_get_person_id(request), campus_id, 'workforce.view_attendance')
    except PermissionDeniedException as e:
        return render(request, 'workforce/home.html', {'error': str(e), 'active_section': 'workforce'})
    except Exception as e:
         return render(request, 'workforce/home.html', {'error': str(e), 'active_section': 'workforce'})

    # Default to today
    today = date.today()
    summary = WorkforceAttendanceQueryService.get_summary_by_range(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        date_from=today,
        date_to=today
    )

    # Calculate basic stats from the summary array
    results = summary.get('results', [])
    present_today = sum(1 for r in results if r['total_in'] > 0)
    
    # We would need to know total staff to calculate 'absent'. 
    # For now, we will mock these high level metrics or query Person with role bindings
    # Real implementation would query UserRoleBinding for staff count
    # Since we can't query kernel freely without a service, we'll put placeholders or query Person naively
    total_staff = Person.objects.count() # Mock for now
    absent = max(0, total_staff - present_today)
    late = 0 # Need shift definitions to calculate late. Placeholder for now.

    context = {
        'total_staff': total_staff,
        'present_today': present_today,
        'absent': absent,
        'late': late,
        'active_section': 'workforce'
    }
    return render(request, 'workforce/home.html', context)

@login_required
def workforce_attendance(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(_get_person_id(request), campus_id, 'workforce.view_attendance')
    except Exception as e:
        return render(request, 'workforce/attendance.html', {'error': str(e), 'active_section': 'workforce'})

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
    else:
        start_date = date.today()

    if end_date:
        end_date = parse_date(end_date)
    else:
        end_date = date.today()

    summary = WorkforceAttendanceQueryService.get_summary_by_range(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        date_from=start_date,
        date_to=end_date
    )

    # Enrich summary with person names from kernel 
    person_ids = [r['person_id'] for r in summary.get('results', [])]
    persons_map = {str(p.id): p.full_name for p in Person.objects.filter(id__in=person_ids)}
    
    enriched_results = []
    for r in summary.get('results', []):
        r['full_name'] = persons_map.get(str(r['person_id']), 'Unknown Staff')
        enriched_results.append(r)

    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'results': enriched_results,
        'active_section': 'workforce'
    }
    return render(request, 'workforce/attendance.html', context)

@login_required
def workforce_log(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(_get_person_id(request), campus_id, 'workforce.view_attendance')
    except Exception as e:
        return render(request, 'workforce/log.html', {'error': str(e), 'active_section': 'workforce'})

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
    else:
        start_date = date.today()
        
    if end_date:
        end_date = parse_date(end_date)
    else:
        end_date = date.today()

    logs = WorkforceAttendanceQueryService.get_event_log_by_range(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        date_from=start_date,
        date_to=end_date
    )

    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'logs': logs,
        'active_section': 'workforce'
    }
    return render(request, 'workforce/log.html', context)

@login_required
def workforce_devices(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(_get_person_id(request), campus_id, 'workforce.view_devices')
    except Exception as e:
        return render(request, 'workforce/devices.html', {'error': str(e), 'active_section': 'workforce'})

    new_token = None

    if request.method == 'POST':
        try:
            # Re-check permission explicitly for manage
            from kernel.services import AuthorizationService
            AuthorizationService.require_permission(_get_person_id(request), campus_id, 'workforce.manage_devices')
            
            name = request.POST.get('name')
            device_type = request.POST.get('device_type', 'TERMINAL')
            ip_address = request.POST.get('ip_address', '127.0.0.1')
            
            device, plain_token = DeviceRegistrationService.register_device(
                person_id=_get_person_id(request),
                campus_id=campus_id,
                name=name,
                device_type=device_type,
                ip_address=ip_address
            )
            # Show the token on the frontend once
            new_token = plain_token
        except Exception as e:
            devices = DeviceRegistrationService.get_devices(campus_id=campus_id, person_id=_get_person_id(request))
            return render(request, 'workforce/devices.html', {
                'error': str(e), 
                'devices': devices, 
                'active_section': 'workforce'
            })

    devices = DeviceRegistrationService.get_devices(campus_id=campus_id, person_id=_get_person_id(request))

    context = {
        'devices': devices,
        'new_token': new_token,
        'active_section': 'workforce'
    }
    return render(request, 'workforce/devices.html', context)
