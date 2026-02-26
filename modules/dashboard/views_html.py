"""
Dashboard HTML Views
Server-rendered template views. Session auth only — no JWT.

Auth flow:
  1. @login_required redirects to /accounts/login/ if no Django session.
  2. campus_id is read from session ('current_campus_id').
     Missing → redirect to select_campus.
  3. Data is fetched directly from service layer — no JSON endpoints.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from kernel.models import Campus, UserRoleBinding
from modules.academics.services import AcademicQueryService
from modules.attendance.models import AttendanceSession
from modules.admissions.models import AdmissionApplication


@login_required
def dashboard_home(request):
    """
    GET /dashboard/

    Renders the main campus dashboard with three key stats:
      - Total students enrolled (active Enrollment records)
      - Active class groups (ClassGroups with active AcademicCycle)
      - Total staff with any active role binding at this campus
    """
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return redirect('kernel:select_campus')

    try:
        campus = Campus.objects.get(id=campus_id)
    except Campus.DoesNotExist:
        # Session is stale — clear and force re-selection
        request.session.pop('current_campus_id', None)
        return redirect('kernel:select_campus')

    student_count = AcademicQueryService.get_enrolled_student_count(campus_id)
    class_count   = AcademicQueryService.get_active_class_group_count(campus_id)

    staff_count = (
        UserRoleBinding.objects
        .filter(
            campus_id=campus_id,
            validity__contains=timezone.now(),
        )
        .values('person_id')
        .distinct()
        .count()
    )

    recent_sessions = (
        AttendanceSession.objects
        .filter(campus_id=campus_id)
        .select_related('class_group', 'taken_by')
        .order_by('-attendance_date')[:5]
    )
    
    recent_applications = (
        AdmissionApplication.objects
        .filter(campus_id=campus_id)
        .order_by('-submitted_at')[:5]
    )

    return render(request, 'dashboard/home.html', {
        'campus':         campus,
        'student_count':  student_count,
        'class_count':    class_count,
        'staff_count':    staff_count,
        'recent_sessions': recent_sessions,
        'recent_applications': recent_applications,
        'generated_at':   timezone.now(),
        'active_section': 'dashboard',
    })
