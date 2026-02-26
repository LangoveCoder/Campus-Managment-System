"""
Academics API Views
Auth: JWT Bearer token → request.person_id (JWTAuthenticationMiddleware)
     Session campus → request.campus_id (CampusContextMiddleware)

Pattern (strict):
  1. 401 if request.person_id is None
  2. 400 if request.campus_id is None
  3. Parse params / body — 400 on malformed
  4. Delegate to service — service handles 403 internally
  5. On exception: PermissionDeniedException/AuthorizationException → 403
                   ValueError/ValidationError → 400
                   everything else → 500 (safe message, full traceback logged)

No raw ORM. Service methods only.
GAP endpoints return 501 and log the missing method.
"""
import json
import logging
from decimal import Decimal, InvalidOperation
from datetime import date

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

from kernel.exceptions import PermissionDeniedException, AuthorizationException

from .services import AcademicQueryService, EnrollmentService, AssessmentService
from .auth import AuthorizationFacade

logger = logging.getLogger(__name__)


# ===========================================================================
# Shared helpers
# ===========================================================================

def _ctx(request):
    """Extract (person_id, campus_id) from middleware-populated request."""
    return getattr(request, 'person_id', None), getattr(request, 'campus_id', None)


def _unauthenticated():
    return JsonResponse(
        {'error': 'Unauthorized', 'detail': 'Valid Bearer token required.'},
        status=401,
    )


def _no_campus():
    return JsonResponse(
        {'error': 'No campus context. Select a campus first.'},
        status=400,
    )


def _bad_request(msg):
    return JsonResponse({'error': msg}, status=400)


def _perm_denied(e):
    return JsonResponse({'error': 'Permission denied', 'detail': str(e)}, status=403)


def _gap(endpoint):
    """501 stub for endpoints whose service method does not yet exist."""
    logger.warning('GAP: No service method for %s', endpoint)
    return JsonResponse(
        {'error': 'Not implemented', 'gap': endpoint,
         'detail': 'Service method missing. Add to the relevant service class.'},
        status=501,
    )


def _handle_service_error(e):
    if isinstance(e, (PermissionDeniedException, AuthorizationException)):
        return _perm_denied(e)
    if isinstance(e, (ValueError, ValidationError)):
        return _bad_request(str(e))
    logger.error('Unexpected error in academics view', exc_info=e)
    return JsonResponse({'error': 'Internal server error.'}, status=500)


def _parse_body(request):
    """Parse JSON body. Returns (body_dict, None) or (None, error_response)."""
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, _bad_request('Invalid JSON body.')


# ===========================================================================
# Serializers  (flat dicts — no nested expansions to avoid N+1)
# ===========================================================================

def _ser_program(p):
    return {
        'id': p.id,
        'name': p.name,
        'code': p.code,
        'program_type': p.program_type,
        'is_active': p.is_active,
    }


def _ser_cycle(c):
    return {
        'id': c.id,
        'name': c.name,
        'sequence': c.sequence,
        'start_date': str(c.start_date) if c.start_date else None,
        'end_date': str(c.end_date) if c.end_date else None,
        'is_active': c.is_active,
    }


def _ser_class_group(cg):
    return {
        'id': cg.id,
        'name': cg.name,
        'section': cg.section,
        'is_active': cg.is_active,
    }


def _ser_student(sp):
    return {
        'id': sp.id,
        'admission_number': sp.admission_number,
        'person_id': str(sp.person_id),
        'full_name': sp.person.full_name,
        'status': sp.status,
    }


def _ser_person(p):
    return {
        'id': str(p.id),
        'full_name': p.full_name,
    }


def _ser_course(c):
    return {
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'is_active': c.is_active,
    }


def _ser_enrollment(e):
    return {
        'id': e.id,
        'student_profile_id': e.student_profile_id,
        'class_group_id': e.class_group_id,
        'enrollment_date': str(e.enrollment_date),
        'status': e.status,
    }


def _ser_assessment_instance(ai):
    return {
        'id': ai.id,
        'class_group_id': ai.class_group_id,
        'assessment_period_id': ai.assessment_period_id,
        'course_offering_id': ai.course_offering_id,
        'max_marks': str(ai.max_marks),
        'scheduled_date': str(ai.scheduled_date) if ai.scheduled_date else None,
        'status': ai.status,
    }


def _ser_result(r):
    return {
        'id': r.id,
        'enrollment_id': r.enrollment_id,
        'assessment_instance_id': r.assessment_instance_id,
        'marks_obtained': str(r.marks_obtained) if r.marks_obtained is not None else None,
        'is_absent': r.is_absent,
    }


# ===========================================================================
# Views — GAP (501)
# ===========================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ProgramListView(View):
    """
    GET api/academics/programs/
    Permission: academics.view_program (enforced here).
    """
    def get(self, request):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            AuthorizationFacade.require(
                person_id=person_id,
                campus_id=campus_id,
                permission_code='academics.view_program',
            )
            programs = AcademicQueryService.get_programs(campus_id=campus_id)
            return JsonResponse({
                'count': programs.count(),
                'results': [_ser_program(p) for p in programs],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class ProgramCyclesView(View):
    """
    GET api/academics/programs/<program_id>/cycles/
    Permission: academics.view_program (enforced here).
    """
    def get(self, request, program_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            AuthorizationFacade.require(
                person_id=person_id,
                campus_id=campus_id,
                permission_code='academics.view_program',
            )
            cycles = AcademicQueryService.get_cycles_for_program(
                program_id=program_id,
                campus_id=campus_id,
            )
            return JsonResponse({
                'program_id': program_id,
                'count': cycles.count(),
                'results': [_ser_cycle(c) for c in cycles],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class CycleClassesView(View):
    """
    GET api/academics/cycles/<cycle_id>/classes/
    Permission: academics.view_program (enforced here).
    """
    def get(self, request, cycle_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            AuthorizationFacade.require(
                person_id=person_id,
                campus_id=campus_id,
                permission_code='academics.view_program',
            )
            classes = AcademicQueryService.get_classes_for_cycle(
                cycle_id=cycle_id,
                campus_id=campus_id,
            )
            return JsonResponse({
                'cycle_id': cycle_id,
                'count': classes.count(),
                'results': [_ser_class_group(cg) for cg in classes],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class EnrollmentDetailView(View):
    """
    GET api/academics/enrollments/<enrollment_id>/
    Permission: academics.view_enrollment (enforced here).
    """
    def get(self, request, enrollment_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            AuthorizationFacade.require(
                person_id=person_id,
                campus_id=campus_id,
                permission_code='academics.view_enrollment',
            )
            enrollment = EnrollmentService.get_enrollment_by_id(
                enrollment_id=enrollment_id,
                campus_id=campus_id,
                person_id=person_id,
            )
            return JsonResponse(_ser_enrollment(enrollment))
        except Exception as e:
            return _handle_service_error(e)


# ===========================================================================
# Views — LIVE
# ===========================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ClassStudentsView(View):
    """
    GET api/academics/classes/<class_group_id>/students/
    Auth enforced internally by AcademicQueryService (academics.view_program).
    """
    def get(self, request, class_group_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            qs = AcademicQueryService.get_students_in_class(
                person_id=person_id,
                class_group_id=class_group_id,
                campus_id=campus_id,
            )
            qs = qs.select_related('person')
            return JsonResponse({
                'class_group_id': class_group_id,
                'count': qs.count(),
                'results': [_ser_student(s) for s in qs],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class ClassTeachersView(View):
    """
    GET api/academics/classes/<class_group_id>/teachers/
    Permission: academics.view_class (enforced here — service has no auth check).
    """
    def get(self, request, class_group_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            AuthorizationFacade.require(
                person_id=person_id,
                campus_id=campus_id,
                permission_code='academics.view_class',
            )
            teachers = AcademicQueryService.get_teachers_for_class(
                class_group_id=class_group_id,
                campus_id=campus_id,
            )
            return JsonResponse({
                'class_group_id': class_group_id,
                'count': teachers.count(),
                'results': [_ser_person(t) for t in teachers],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class ClassCoursesView(View):
    """
    GET api/academics/classes/<class_group_id>/courses/
    Permission: academics.view_class (enforced here — service has no auth check).
    """
    def get(self, request, class_group_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            AuthorizationFacade.require(
                person_id=person_id,
                campus_id=campus_id,
                permission_code='academics.view_class',
            )
            courses = AcademicQueryService.get_courses_for_class(
                class_group_id=class_group_id,
                campus_id=campus_id,
            )
            return JsonResponse({
                'class_group_id': class_group_id,
                'count': courses.count(),
                'results': [_ser_course(c) for c in courses],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class EnrollView(View):
    """
    POST api/academics/enroll/
    Body: { student_profile_id, class_group_id }
    Auth enforced by EnrollmentService (academics.enroll_student).
    """
    def post(self, request):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        body, err = _parse_body(request)
        if err:
            return err

        student_profile_id = body.get('student_profile_id')
        class_group_id = body.get('class_group_id')
        if not student_profile_id or not class_group_id:
            return _bad_request('Required: student_profile_id, class_group_id')

        try:
            student_profile_id = int(student_profile_id)
            class_group_id = int(class_group_id)
        except (TypeError, ValueError):
            return _bad_request('student_profile_id and class_group_id must be integers.')

        try:
            enrollment = EnrollmentService.create_enrollment(
                student_profile_id=student_profile_id,
                class_group_id=class_group_id,
                campus_id=campus_id,
                person_id=person_id,
            )
            return JsonResponse(_ser_enrollment(enrollment), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class AssessmentCreateView(View):
    """
    POST api/academics/assessments/create/
    Body: { class_group_id, assessment_period_id, course_offering_id, max_marks, [scheduled_date] }
    Auth enforced by AssessmentService (academics.create_program — approximate).
    """
    def post(self, request):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        body, err = _parse_body(request)
        if err:
            return err

        required_fields = ['class_group_id', 'assessment_period_id', 'course_offering_id', 'max_marks']
        missing = [f for f in required_fields if body.get(f) is None]
        if missing:
            return _bad_request(f'Missing required fields: {", ".join(missing)}')

        try:
            class_group_id      = int(body['class_group_id'])
            assessment_period_id = int(body['assessment_period_id'])
            course_offering_id  = int(body['course_offering_id'])
            max_marks           = Decimal(str(body['max_marks']))
            raw_date            = body.get('scheduled_date')
            scheduled_date      = date.fromisoformat(raw_date) if raw_date else None
        except (TypeError, ValueError, InvalidOperation) as e:
            return _bad_request(f'Invalid field value: {e}')

        try:
            instance = AssessmentService.create_assessment_instance(
                class_group_id=class_group_id,
                assessment_period_id=assessment_period_id,
                course_offering_id=course_offering_id,
                max_marks=max_marks,
                scheduled_date=scheduled_date,
                campus_id=campus_id,
                person_id=person_id,
            )
            return JsonResponse(_ser_assessment_instance(instance), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class AssessmentResultEntryView(View):
    """
    POST api/academics/assessments/<instance_id>/results/
    Body: { enrollment_id, marks_obtained }
    Auth enforced by AssessmentService (academics.enter_assessment_result).
    """
    def post(self, request, instance_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        body, err = _parse_body(request)
        if err:
            return err

        enrollment_id = body.get('enrollment_id')
        marks_obtained = body.get('marks_obtained')
        if enrollment_id is None or marks_obtained is None:
            return _bad_request('Required: enrollment_id, marks_obtained')

        try:
            enrollment_id  = int(enrollment_id)
            marks_obtained = Decimal(str(marks_obtained))
        except (TypeError, ValueError, InvalidOperation) as e:
            return _bad_request(f'Invalid field value: {e}')

        try:
            result = AssessmentService.enter_result(
                enrollment_id=enrollment_id,
                assessment_instance_id=int(instance_id),
                marks_obtained=marks_obtained,
                entered_by_person_id=person_id,
                campus_id=campus_id,
            )
            return JsonResponse(_ser_result(result), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class ClassResultsSummaryView(View):
    """
    GET api/academics/classes/<class_group_id>/results/?assessment_instance_id=<id>
    Auth enforced by AssessmentService (academics.view_student_results).
    """
    def get(self, request, class_group_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        assessment_instance_id = request.GET.get('assessment_instance_id')
        if not assessment_instance_id:
            return _bad_request('Required query param: assessment_instance_id')

        try:
            assessment_instance_id = int(assessment_instance_id)
        except ValueError:
            return _bad_request('assessment_instance_id must be an integer.')

        try:
            summary = AssessmentService.get_results_summary_by_class(
                person_id=person_id,
                campus_id=campus_id,
                class_group_id=class_group_id,
                assessment_instance_id=assessment_instance_id,
            )
            return JsonResponse({
                'class_group_id': class_group_id,
                'assessment_instance_id': assessment_instance_id,
                **summary,
            })
        except Exception as e:
            return _handle_service_error(e)
