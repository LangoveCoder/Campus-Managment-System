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
                campus_id = request.POST.get('campus_id') or 1
                application = AdmissionsService.submit_application(
                    full_name=full_name,
                    dob=request.POST.get('date_of_birth') or '2000-01-01',
                    campus_id=int(campus_id),
                    form_payload={'full_name': full_name},
                    father_name=request.POST.get('father_name', ''),
                    cnic=request.POST.get('cnic', ''),
                    district=request.POST.get('district', ''),
                    marks=request.POST.get('marks') or None,
                    date_of_birth=request.POST.get('date_of_birth') or None,
                    contact_number=request.POST.get('contact_number', ''),
                    address=request.POST.get('address', ''),
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
    
    from modules.admissions.utils import format_cnic
    for app in applications:
        app.formatted_cnic = format_cnic(app.cnic)
    
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
                program_id = request.POST.get('program_id')
                class_group_id = request.POST.get('class_group_id') or None
                AdmissionsService.convert_to_enrollment(
                    person_id=_get_person_id(request),
                    application_id=application.id,
                    program_id=program_id,
                    class_group_id=class_group_id
                )
                return redirect('application_detail', app_id=app_id)
        except Exception as e:
            return render(request, 'admissions/detail.html', {
                'application': application,
                'error': str(e),
                'active_section': 'admissions'
            })

    from modules.academics.models import AcademicProgram, ClassGroup
    programs = AcademicProgram.objects.filter(campus_id=campus_id)
    class_groups = ClassGroup.objects.filter(campus_id=campus_id, is_active=True).select_related('academic_cycle__academic_program')
    from modules.admissions.utils import format_cnic
    application.formatted_cnic = format_cnic(application.cnic)
    return render(request, 'admissions/detail.html', {
        'application': application,
        'programs': programs,
        'class_groups': class_groups,
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

# Screen 5: Import Merit List
@login_required
def import_merit_list(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(person_id=_get_person_id(request), campus_id=campus_id, permission_code='admissions.make_decision')
    except Exception as e:
        return render(request, 'admissions/import_merit_list.html', {'error': str(e), 'active_section': 'admissions'})

    if request.method == 'POST':
        # Placeholder for CSV upload / Merit List processing
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            return render(request, 'admissions/import_merit_list.html', {
                'error': 'Please upload a CSV file.',
                'active_section': 'admissions'
            })
            
        try:
            import io, csv
            result = AdmissionsService.process_merit_list(
                person_id=_get_person_id(request),
                campus_id=campus_id,
                csv_file=csv_file
            )
            
            msg = f"Merit list imported successfully. {result['imported']} imported, {result['skipped']} skipped (duplicate CNIC or missing data)."
            if False:
                pass
                
            return render(request, 'admissions/import_merit_list.html', {
                'success': True,
                'message': msg,
                'active_section': 'admissions'
            })
        except Exception as e:
            return render(request, 'admissions/import_merit_list.html', {
                'error': str(e),
                'active_section': 'admissions'
            })

    return render(request, 'admissions/import_merit_list.html', {
        'active_section': 'admissions'
    })

# Screen 6: Admission Config
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
@login_required
def admission_config(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
        
    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(person_id=_get_person_id(request), campus_id=campus_id, permission_code='admissions.make_decision')
    except Exception as e:
        return render(request, 'admissions/admission_config.html', {'error': str(e), 'active_section': 'admissions'})

    from modules.admissions.models import AdmissionConfig
    from modules.academics.models import AcademicProgram
    
    programs = AcademicProgram.objects.filter(campus_id=campus_id)
    
    if request.method == 'POST':
        try:
            prog_id = request.POST.get('program_id')
            if prog_id == '':
                prog_id = None
            
            config, _ = AdmissionConfig.objects.get_or_create(
                campus_id=campus_id,
                academic_program_id=prog_id
            )
            
            config.interview_type = request.POST.get('interview_type', 'QUALIFYING')
            config.test_weight = request.POST.get('test_weight') or 1.00
            config.interview_weight = request.POST.get('interview_weight') or 0.00
            config.save()
            
            return render(request, 'admissions/admission_config.html', {
                'success': True,
                'message': 'Configuration saved successfully.',
                'programs': programs,
                'active_section': 'admissions'
            })
        except Exception as e:
            return render(request, 'admissions/admission_config.html', {
                'error': str(e),
                'programs': programs,
                'active_section': 'admissions'
            })
            
    return render(request, 'admissions/admission_config.html', {
        'programs': programs,
        'active_section': 'admissions'
    })

# Screen 7: Merit List Rankings
@login_required
def merit_list_view(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
        
    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(person_id=_get_person_id(request), campus_id=campus_id, permission_code='admissions.make_decision')
    except Exception as e:
        return render(request, 'admissions/merit_list.html', {'error': str(e), 'active_section': 'admissions'})
        
    from modules.admissions.models import AdmissionApplication
    from modules.admissions.services import AdmissionsService
    
    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        action = request.POST.get('action')
        try:
            app = AdmissionApplication.objects.get(id=app_id, campus_id=campus_id)
            if action == 'accept':
                app.status = AdmissionApplication.Status.ACCEPTED
            elif action == 'reject':
                app.status = AdmissionApplication.Status.REJECTED
            elif action == 'waitlist':
                app.status = AdmissionApplication.Status.WAITLISTED
            app.save()
            return redirect('merit_list')
        except Exception as e:
            pass # ignore for simplicity
            
    apps = AdmissionApplication.objects.filter(
        campus_id=campus_id, 
        status=AdmissionApplication.Status.INTERVIEW_PASSED
    )
    
    for a in apps:
        AdmissionsService.calculate_merit_score(a.id, campus_id)
        
    # Re-fetch to get updated scores and sort
    apps = AdmissionApplication.objects.filter(
        campus_id=campus_id, 
        status=AdmissionApplication.Status.INTERVIEW_PASSED
    ).order_by('-merit_score')
    
    return render(request, 'admissions/merit_list.html', {
        'applications': apps,
        'active_section': 'admissions'
    })

# Screen 8: Record Interview
@login_required
def record_interview(request, app_id):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
        
    try:
        from kernel.services import AuthorizationService
        AuthorizationService.require_permission(person_id=_get_person_id(request), campus_id=campus_id, permission_code='admissions.conduct_interview')
        
        from modules.admissions.services import AdmissionsService
        application = AdmissionsService.get_application_by_id(app_id, campus_id, _get_person_id(request))
    except Exception as e:
        return render(request, 'admissions/record_interview.html', {'error': str(e), 'active_section': 'admissions'})

    from modules.admissions.models import AdmissionConfig
    config = AdmissionConfig.objects.filter(
        campus_id=campus_id,
        academic_program=application.academic_program
    ).first() or AdmissionConfig.objects.filter(
        campus_id=campus_id,
        academic_program=None
    ).first()
    
    is_scored = config.interview_type == 'SCORED' if config else False

    if request.method == 'POST':
        try:
            remarks = request.POST.get('remarks')
            recommendation = request.POST.get('recommendation')
            interview_marks = request.POST.get('interview_marks')
            
            if recommendation == 'Pass':
                application.status = application.Status.INTERVIEW_PASSED
            elif recommendation == 'Fail':
                application.status = application.Status.REJECTED
            else:
                application.status = application.Status.INTERVIEWED
                
            if is_scored and interview_marks:
                application.interview_marks = float(interview_marks)
                
            application.save()
            
            return redirect('application_detail', app_id=app_id)
        except Exception as e:
            return render(request, 'admissions/record_interview.html', {
                'application': application,
                'is_scored': is_scored,
                'error': str(e),
                'active_section': 'admissions'
            })

    return render(request, 'admissions/record_interview.html', {
        'application': application,
        'is_scored': is_scored,
        'active_section': 'admissions'
    })
