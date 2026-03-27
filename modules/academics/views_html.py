from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from kernel.facades import AuthorizationFacade
from .services.academic_query_service import AcademicQueryService
from .services.enrollment_service import EnrollmentService
from .services.assessment_service import AssessmentService
from .models import AcademicProgram, ClassGroup, AssessmentInstance

def get_campus_context(request: HttpRequest):
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return None
    return int(campus_id)

def _get_person_id(request: HttpRequest):
    person = getattr(request.user, 'person', None)
    return str(person.id) if person else None

@login_required
def program_list(request: HttpRequest) -> HttpResponse:
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
    
    AuthorizationFacade.require(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        permission_code='academics.view_program'
    )
    
    programs = AcademicQueryService.get_programs(campus_id=campus_id)
    
    return render(request, 'program_list.html', {
        'programs': programs,
        'active_section': 'academics'
    })

@login_required
def program_detail(request: HttpRequest, program_id: int) -> HttpResponse:
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
    
    AuthorizationFacade.require(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        permission_code='academics.view_program'
    )
    
    program = get_object_or_404(AcademicProgram, id=program_id, campus_id=campus_id)
    cycles = AcademicQueryService.get_cycles_for_program(program_id=program_id, campus_id=campus_id)
    
    # Pre-fetch classes for each cycle to avoid template hits
    cycle_data = []
    for cycle in cycles:
        classes = AcademicQueryService.get_classes_for_cycle(cycle_id=cycle.id, campus_id=campus_id)
        cycle_data.append({
            'cycle': cycle,
            'classes': classes
        })
    
    return render(request, 'program_detail.html', {
        'program': program,
        'cycle_data': cycle_data,
        'active_section': 'academics'
    })

@login_required
def class_detail(request: HttpRequest, class_group_id: int) -> HttpResponse:
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
    
    AuthorizationFacade.require(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        permission_code='academics.view_class'
    )
    
    class_group = get_object_or_404(ClassGroup, id=class_group_id, campus_id=campus_id)
    students = AcademicQueryService.get_students_in_class(
        person_id=_get_person_id(request),
        class_group_id=class_group_id,
        campus_id=campus_id
    )
    teachers = AcademicQueryService.get_teachers_for_class(
        class_group_id=class_group_id,
        campus_id=campus_id
    )
    courses = AcademicQueryService.get_courses_for_class(
        class_group_id=class_group_id,
        campus_id=campus_id
    )
    
    from modules.campus_identity.models import CampusPerson
    campus_persons = CampusPerson.objects.filter(campus_id=campus_id)
    identifier_map = {str(cp.person_id): cp.campus_identifier for cp in campus_persons}

    return render(request, 'class_detail.html', {
        'class_group': class_group,
        'program_name': class_group.academic_cycle.academic_program.name,
        'students': students,
        'teachers': teachers,
        'courses': courses,
        'active_section': 'academics',
        'identifier_map': identifier_map,
    })

@login_required
def enroll_student(request: HttpRequest) -> HttpResponse:
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
    
    if request.method == 'POST':
        AuthorizationFacade.require(
            person_id=_get_person_id(request),
            campus_id=campus_id,
            permission_code='academics.enroll_student'
        )
        
        student_person_id = request.POST.get('student_person_id')
        class_group_id = request.POST.get('class_group_id')
        
        try:
            # Need to find the StudentProfile for this Person
            from kernel.models import Person
            from django.core.exceptions import ValidationError
            try:
                person = Person.objects.get(id=student_person_id)
            except (Person.DoesNotExist, ValidationError):
                messages.error(request, f"Person with ID {student_person_id} does not exist or is invalid.")
                return redirect('enroll_student')
                
            student_profile = person.student_profiles.filter(campus_id=campus_id).first()
            
            if not student_profile:
                messages.error(request, f"No student profile found for Person {student_person_id} at this campus.")
                return redirect('enroll_student')

            EnrollmentService.create_enrollment(
                student_profile_id=student_profile.id,
                class_group_id=class_group_id,
                campus_id=campus_id,
                person_id=_get_person_id(request)
            )
            messages.success(request, "Student enrolled successfully.")
            return redirect('class_detail', class_group_id=class_group_id)
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('enroll_student')
    
    # GET
    AuthorizationFacade.require(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        permission_code='academics.view_class'
    )
    
    # Get all active classes for the dropdown
    # Note: query_service doesn't have a broad 'get_all_classes' but we can use the model directly or cycles
    programs = AcademicQueryService.get_programs(campus_id=campus_id)
    all_classes = []
    for p in programs:
        cycles = AcademicQueryService.get_cycles_for_program(program_id=p.id, campus_id=campus_id)
        for c in cycles:
            classes = AcademicQueryService.get_classes_for_cycle(cycle_id=c.id, campus_id=campus_id)
            for cl in classes:
                all_classes.append(cl)
                
    return render(request, 'enroll.html', {
        'classes': all_classes,
        'active_section': 'academics'
    })

@login_required
def class_results(request: HttpRequest, class_group_id: int) -> HttpResponse:
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')
        
    AuthorizationFacade.require(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        permission_code='academics.view_student_results'
    )
    
    class_group = get_object_or_404(ClassGroup, id=class_group_id, campus_id=campus_id)
    instances = AssessmentInstance.objects.filter(
        class_group_id=class_group_id, 
        campus_id=campus_id
    ).select_related('course_offering__course', 'assessment_period')
    
    instance_id = request.GET.get('instance_id')
    summary = None
    if instance_id:
        summary = AssessmentService.get_results_summary_by_class(
            person_id=_get_person_id(request),
            campus_id=campus_id,
            class_group_id=class_group_id,
            assessment_instance_id=int(instance_id)
        )
        
    return render(request, 'academics/results.html', {
        'class_group': class_group,
        'instances': instances,
        'summary': summary,
        'active_section': 'academics'
    })
