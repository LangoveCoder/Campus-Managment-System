"""
Dashboard HTML Views
Server-rendered template views. Session auth only — no JWT.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from kernel.models import Campus, UserRoleBinding
from modules.academics.services import AcademicQueryService
from modules.attendance.services.attendance_service import AttendanceQueryService
from modules.admissions.services.admissions_service import AdmissionsService


def _get_person_id(request):
    person = getattr(request.user, 'person', None)
    return str(person.id) if person else None


@login_required
def dashboard_home(request):
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return redirect('kernel:select_campus')
    try:
        campus = Campus.objects.get(id=campus_id)
    except Campus.DoesNotExist:
        request.session.pop('current_campus_id', None)
        return redirect('kernel:select_campus')

    person_id = _get_person_id(request)

    student_count = AcademicQueryService.get_enrolled_student_count(campus_id)
    class_count = AcademicQueryService.get_active_class_group_count(campus_id)
    staff_count = (
        UserRoleBinding.objects
        .filter(campus_id=campus_id, validity__contains=timezone.now())
        .values('person_id')
        .distinct()
        .count()
    )

    try:
        recent_sessions = AttendanceQueryService.get_recent_sessions(person_id, campus_id, limit=5)
    except Exception:
        recent_sessions = []

    try:
        recent_applications = AdmissionsService.get_applications(campus_id, person_id)[:5]
    except Exception:
        recent_applications = []

    return render(request, 'dashboard/home.html', {
        'campus': campus,
        'student_count': student_count,
        'class_count': class_count,
        'staff_count': staff_count,
        'recent_sessions': recent_sessions,
        'recent_applications': recent_applications,
        'generated_at': timezone.now(),
        'active_section': 'dashboard',
    })
