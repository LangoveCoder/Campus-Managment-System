"""
Dashboard Views
Read-only. Permission-gated. JSON-only responses. No templates.

Authentication: JWT Bearer token via JWTAuthenticationMiddleware.
  - All views check request.person_id first (set by middleware).
  - 401 if no valid token. 403 if valid token but missing permission.

Data sources per view:
  DashboardHomeView      → AcademicQueryService + kernel models (Campus, UserRoleBinding)
  AttendanceSummaryView  → AttendanceQueryService only
  AssessmentSummaryView  → AssessmentService only
"""
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from kernel.models import Campus, UserRoleBinding
from kernel.exceptions import PermissionDeniedException, AuthorizationException

from modules.academics.services import AcademicQueryService, AssessmentService
from modules.attendance.services import AttendanceQueryService

from .auth import AuthorizationFacade


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_request_context(request):
    """
    Extract (person_id, campus_id) from request.
    person_id  — set by JWTAuthenticationMiddleware from Bearer token.
    campus_id  — set by CampusContextMiddleware from session ('current_campus_id').
    """
    person_id = getattr(request, 'person_id', None)
    campus_id = getattr(request, 'campus_id', None)   # set by CampusContextMiddleware
    return person_id, campus_id


def _unauthenticated():
    return JsonResponse(
        {'error': 'Unauthorized', 'detail': 'Valid Bearer token required.'},
        status=401,
    )


def _permission_denied(e):
    return JsonResponse(
        {'error': 'Permission denied', 'detail': str(e)},
        status=403,
    )


def _bad_request(msg):
    return JsonResponse({'error': msg}, status=400)


def _not_found(msg):
    return JsonResponse({'error': msg}, status=404)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class DashboardHomeView(View):
    """
    GET api/dashboard/home/

    Campus-level summary.
    Requires: Bearer token with academics.view_program permission.
    """

    def get(self, request):
        person_id, campus_id = _get_request_context(request)

        if not person_id:
            return _unauthenticated()

        if not campus_id:
            return _bad_request('No campus context. Select a campus first.')

        try:
            AuthorizationFacade.require(person_id, campus_id, 'academics.view_program')
        except (PermissionDeniedException, AuthorizationException) as e:
            return _permission_denied(e)

        try:
            campus = Campus.objects.get(id=campus_id)
        except Campus.DoesNotExist:
            return _not_found('Campus not found.')

        active_persons_count = (
            UserRoleBinding.objects
            .filter(
                campus_id=campus_id,
                validity__contains=timezone.now(),
            )
            .values('person_id')
            .distinct()
            .count()
        )

        enrolled_student_count = AcademicQueryService.get_enrolled_student_count(campus_id)
        active_class_group_count = AcademicQueryService.get_active_class_group_count(campus_id)

        return JsonResponse({
            'campus': {
                'id': campus.id,
                'name': campus.name,
            },
            'active_persons_at_campus': active_persons_count,
            'total_students_enrolled': enrolled_student_count,
            'total_active_class_groups': active_class_group_count,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AttendanceSummaryView(View):
    """
    GET api/dashboard/attendance/
    Query params: class_group_id, date_from (YYYY-MM-DD), date_to (YYYY-MM-DD)

    Requires: Bearer token with attendance.view_attendance permission.
    """

    def get(self, request):
        person_id, campus_id = _get_request_context(request)

        if not person_id:
            return _unauthenticated()

        if not campus_id:
            return _bad_request('No campus context. Select a campus first.')

        class_group_id = request.GET.get('class_group_id')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        if not all([class_group_id, date_from, date_to]):
            return _bad_request('Required params: class_group_id, date_from, date_to')

        try:
            class_group_id = int(class_group_id)
        except ValueError:
            return _bad_request('class_group_id must be an integer.')

        try:
            summary = AttendanceQueryService.get_summary_by_class_and_date_range(
                person_id=person_id,
                campus_id=campus_id,
                class_group_id=class_group_id,
                date_from=date_from,
                date_to=date_to,
            )
        except (PermissionDeniedException, AuthorizationException) as e:
            return _permission_denied(e)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'class_group_id': class_group_id,
            'date_from': date_from,
            'date_to': date_to,
            **summary,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AssessmentSummaryView(View):
    """
    GET api/dashboard/assessments/
    Query params: class_group_id, assessment_instance_id

    Requires: Bearer token with academics.view_student_results permission.
    """

    def get(self, request):
        person_id, campus_id = _get_request_context(request)

        if not person_id:
            return _unauthenticated()

        if not campus_id:
            return _bad_request('No campus context. Select a campus first.')

        class_group_id = request.GET.get('class_group_id')
        assessment_instance_id = request.GET.get('assessment_instance_id')

        if not all([class_group_id, assessment_instance_id]):
            return _bad_request('Required params: class_group_id, assessment_instance_id')

        try:
            class_group_id = int(class_group_id)
            assessment_instance_id = int(assessment_instance_id)
        except ValueError:
            return _bad_request('class_group_id and assessment_instance_id must be integers.')

        try:
            summary = AssessmentService.get_results_summary_by_class(
                person_id=person_id,
                campus_id=campus_id,
                class_group_id=class_group_id,
                assessment_instance_id=assessment_instance_id,
            )
        except (PermissionDeniedException, AuthorizationException) as e:
            return _permission_denied(e)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'class_group_id': class_group_id,
            'assessment_instance_id': assessment_instance_id,
            **summary,
        })
