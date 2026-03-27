import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from kernel.exceptions import PermissionDeniedException
from .services.admissions_service import AdmissionsService
from .models import AdmissionApplication

def get_campus_context(request):
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return None
    return int(campus_id)

def _get_person_id(request):
    person = getattr(request.user, 'person', None)
    return str(person.id) if person else None

# Screen 0: Public Apply Form
def apply(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        if full_name:
            try:
                application = AdmissionsService.submit_application(
                    full_name=full_name,
                    dob='2000-01-01',  # Default/mock value to satisfy signature
                    campus_id=1,       # Defaulting to 1 for public generic form
                    form_payload={'full_name': full_name}
                )
                return render(request, 'admissions/apply.html', {
                    'success': True,
                    'application_id': application.id,
                })
            except Exception as e:
                return render(request, 'admissions/apply.html', {
                    'error': str(e),
                })
        else:
            return render(request, 'admissions/apply.html', {
                'error': 'Full name is required.',
            })
    return render(request, 'admissions/apply.html')

# Screen 1: Applications List
@login_required
def applications_list(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(person_id=_get_person_id(request), campus_id=campus_id, permission_code='admissions.view_application')
    except PermissionDeniedException as e:
        return render(request, 'admissions/list.html', {'error': str(e), 'active_section': 'admissions'})
    except Exception as e:
        return render(request, 'admissions/list.html', {'error': "A permission error occurred: " + str(e), 'active_section': 'admissions'})

    applications = AdmissionsService.get_applications(campus_id, _get_person_id(request))
    
    from modules.campus_identity.models import CampusPerson
    campus_persons = CampusPerson.objects.filter(campus_id=campus_id)
    identifier_map = {str(cp.person_id): cp.campus_identifier for cp in campus_persons}
    
    return render(request, 'admissions/list.html', {
        'applications': applications,
        'active_section': 'admissions',
        'identifier_map': identifier_map,
    })

# Screen 2: Application Detail
@login_required
def application_detail(request, app_id):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
        
    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(person_id=_get_person_id(request), campus_id=campus_id, permission_code='admissions.view_application')
        application = AdmissionsService.get_application_by_id(app_id, campus_id, _get_person_id(request))
    except Exception as e:
        return render(request, 'admissions/detail.html', {'error': str(e), 'active_section': 'admissions'})

    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            if action == 'schedule_interview':
                # Simplified representation of an interview to advance state
                AdmissionsService.conduct_interview(
                    person_id=_get_person_id(request),
                    application_id=application.id,
                    remarks="Fast-tracked interview confirmation",
                    recommendation="Proceed"
                )
                return redirect('application_detail', app_id=app_id)
            elif action == 'convert':
                AdmissionsService.convert_to_enrollment(
                    person_id=_get_person_id(request),
                    application_id=application.id
                )
                return redirect('application_detail', app_id=app_id)
        except Exception as e:
            return render(request, 'admissions/detail.html', {
                'application': application,
                'error': str(e),
                'active_section': 'admissions'
            })

    return render(request, 'admissions/detail.html', {
        'application': application,
        'active_section': 'admissions'
    })

# Screen 3: Record Test Result
@login_required
def test_result(request, app_id):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(person_id=_get_person_id(request), campus_id=campus_id, permission_code='admissions.record_test_result')
        application = AdmissionsService.get_application_by_id(app_id, campus_id, _get_person_id(request))
    except Exception as e:
        return render(request, 'admissions/test_result.html', {'error': str(e), 'active_section': 'admissions'})

    if request.method == 'POST':
        try:
            score = float(request.POST.get('score', 0))
            # Test recording advances state if it's strictly SUBMITTED.
            AdmissionsService.evaluate_test_result(
                person_id=_get_person_id(request),
                application_id=application.id,
                score=score
            )
            return redirect('application_detail', app_id=app_id)
        except Exception as e:
             return render(request, 'admissions/test_result.html', {
                'application': application,
                'error': str(e),
                'active_section': 'admissions',
                'applicant_name': application.form_payload.get('full_name', 'Unknown')
            })

    return render(request, 'admissions/test_result.html', {
        'application': application,
        'active_section': 'admissions',
        'applicant_name': application.form_payload.get('full_name', 'Unknown')
    })

# Screen 4: Make Decision
@login_required
def make_decision(request, app_id):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(person_id=_get_person_id(request), campus_id=campus_id, permission_code='admissions.make_decision')
        application = AdmissionsService.get_application_by_id(app_id, campus_id, _get_person_id(request))
    except Exception as e:
        return render(request, 'admissions/decision.html', {'error': str(e), 'active_section': 'admissions'})

    if request.method == 'POST':
        try:
            decision = request.POST.get('decision')
            notes = request.POST.get('notes', '')
            AdmissionsService.make_decision(
                person_id=_get_person_id(request),
                application_id=application.id,
                decision=decision,
                comments=notes
            )
            return redirect('application_detail', app_id=app_id)
        except Exception as e:
             return render(request, 'admissions/decision.html', {
                'application': application,
                'error': str(e),
                'active_section': 'admissions'
            })

    return render(request, 'admissions/decision.html', {
        'application': application,
        'active_section': 'admissions'
    })
