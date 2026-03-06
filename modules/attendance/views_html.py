from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

def get_campus_context(request):
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return None
    return int(campus_id)

def _get_person_id(request):
    person = getattr(request.user, 'person', None)
    return str(person.id) if person else None

from kernel.facades import AuthorizationFacade
from modules.attendance.services.attendance_service import (
    AttendanceSessionService, 
    AttendanceMarkingService, 
    AttendanceQueryService
)
from modules.academics.services.academic_query_service import AcademicQueryService

@login_required
def attendance_home(request):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    AuthorizationFacade.require(_get_person_id(request), campus_id, 'attendance.view_attendance')

    # Gather class groups via academic query service to avoid direct ORM when possible
    programs = AcademicQueryService.get_programs(campus_id)
    class_groups = []
    for program in programs:
        cycles = AcademicQueryService.get_cycles_for_program(program.id, campus_id)
        for cycle in cycles:
            classes = AcademicQueryService.get_classes_for_cycle(cycle.id, campus_id)
            for cg in classes:
                class_groups.append(cg)

    return render(request, 'attendance/home.html', {
        'class_groups': class_groups,
        'active_section': 'attendance'
    })

@login_required
def mark_attendance(request, class_group_id):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    # Verify class group exists in this campus (we do allow get_object_or_404 for basic scoping)
    class_group = AcademicQueryService.get_class_group_by_id(class_group_id, campus_id)
    if class_group is None:
        from django.http import Http404
        raise Http404

    if request.method == 'POST':
        AuthorizationFacade.require(_get_person_id(request), campus_id, 'attendance.mark_attendance')
        
        attendance_date = request.POST.get('attendance_date')
        if not attendance_date:
            attendance_date = timezone.now().date()
            
        students = AcademicQueryService.get_students_in_class(_get_person_id(request), class_group_id, campus_id)
        
        attendance_data = []
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'ABSENT') # default to absent
            attendance_data.append({
                'student_id': student.id,  # Record links to StudentProfile, not Person
                'status': status
            })

        try:
            session = AttendanceSessionService.create_session(
                person_id=_get_person_id(request),
                campus_id=campus_id,
                class_group_id=class_group_id,
                attendance_date=attendance_date,
                session_type='DAILY',
                source='MANUAL'
            )
            
            AttendanceMarkingService.mark_bulk(
                person_id=_get_person_id(request),
                campus_id=campus_id,
                session_id=session.id,
                attendance_data=attendance_data
            )
            return redirect('attendance_summary', class_group_id=class_group_id)
        except Exception as e:
            error_message = str(e)
            students = AcademicQueryService.get_students_in_class(_get_person_id(request), class_group_id, campus_id)
            return render(request, 'attendance/mark.html', {
                'class_group': class_group,
                'students': students,
                'today': timezone.now().date().isoformat(),
                'active_section': 'attendance',
                'error_message': error_message
            })

    # GET Request
    AuthorizationFacade.require(_get_person_id(request), campus_id, 'attendance.view_attendance')
    students = AcademicQueryService.get_students_in_class(_get_person_id(request), class_group_id, campus_id)
    
    return render(request, 'attendance/mark.html', {
        'class_group': class_group,
        'students': students,
        'today': timezone.now().date().isoformat(),
        'active_section': 'attendance'
    })

@login_required
def attendance_summary(request, class_group_id):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    AuthorizationFacade.require(_get_person_id(request), campus_id, 'attendance.view_attendance')
    class_group = AcademicQueryService.get_class_group_by_id(class_group_id, campus_id)
    if class_group is None:
        from django.http import Http404
        raise Http404

    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    
    if date_to_str:
        date_to = timezone.datetime.strptime(date_to_str, '%Y-%m-%d').date()
    else:
        date_to = timezone.now().date()
        
    if date_from_str:
        date_from = timezone.datetime.strptime(date_from_str, '%Y-%m-%d').date()
    else:
        date_from = date_to - timedelta(days=30)

    summary = AttendanceQueryService.get_summary_by_class_and_date_range(
        person_id=_get_person_id(request),
        campus_id=campus_id,
        class_group_id=class_group_id,
        date_from=date_from,
        date_to=date_to
    )

    return render(request, 'attendance/summary.html', {
        'class_group': class_group,
        'summary': summary,
        'date_from': date_from.isoformat(),
        'date_to': date_to.isoformat(),
        'active_section': 'attendance'
    })

@login_required
def session_list(request, class_group_id):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    class_group = AcademicQueryService.get_class_group_by_id(class_group_id, campus_id)
    if class_group is None:
        from django.http import Http404
        raise Http404
    sessions = AttendanceQueryService.get_sessions_for_class(_get_person_id(request), campus_id, class_group_id)

    return render(request, 'attendance/sessions_list.html', {
        'class_group': class_group,
        'sessions': sessions,
        'active_section': 'attendance'
    })


@login_required
def student_history(request, enrollment_id):
    campus_id = get_campus_context(request)
    if not campus_id:
        return redirect('select_campus')

    enrollment = AcademicQueryService.get_enrollment_by_id(enrollment_id, campus_id)
    if enrollment is None:
        from django.http import Http404
        raise Http404
    history_data = AttendanceQueryService.get_student_attendance_history(_get_person_id(request), campus_id, enrollment_id)

    return render(request, 'attendance/student_history.html', {
        'enrollment': enrollment,
        'records': history_data['records'],
        'summary': history_data['summary'],
        'active_section': 'attendance'
    })
