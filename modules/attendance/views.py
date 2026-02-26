"""
Attendance API Views
Auth: JWT Bearer token → request.person_id (JWTAuthenticationMiddleware)
     Session campus → request.campus_id (CampusContextMiddleware)

Pattern (same as academics/admissions):
  1. 401 if request.person_id is None (all endpoints — no exceptions)
  2. 400 if request.campus_id is None
  3. Parse JSON body — 400 on malformed
  4. Delegate to service — service handles 403 internally
  5. PermissionDeniedException → 403, ValidationError/BusinessRuleViolation → 400, else → 500

Auth facade note:
  attendance.auth.AuthorizationFacade PREPENDS 'attendance.' automatically.
  All permission checks are delegated to the service — no view-level AuthorizationFacade calls needed.

Permission code mismatch (documented, not fixed here — no service modification allowed):
  create_session view spec says 'manage_attendance' but
  AttendanceSessionService.create_session() enforces 'attendance.create_session' internally.

Body shape note:
  API body uses 'person_id' for student identifier; the service dict key is 'student_id'.
  Views translate: person_id → student_id before passing to mark_bulk().
"""
import json
import logging
from datetime import date

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

from kernel.exceptions import PermissionDeniedException, AuthorizationException, BusinessRuleViolation

from .services.attendance_service import (
    AttendanceSessionService,
    AttendanceMarkingService,
    AttendanceQueryService,
)

logger = logging.getLogger(__name__)


# ===========================================================================
# Shared helpers
# ===========================================================================

def _ctx(request):
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


def _handle_service_error(e):
    if isinstance(e, (PermissionDeniedException, AuthorizationException)):
        return JsonResponse({'error': 'Permission denied', 'detail': str(e)}, status=403)
    if isinstance(e, (ValueError, ValidationError, BusinessRuleViolation)):
        return JsonResponse({'error': str(e)}, status=400)
    logger.error('Unexpected error in attendance view', exc_info=e)
    return JsonResponse({'error': 'Internal server error.'}, status=500)


def _parse_body(request):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, _bad_request('Invalid JSON body.')


# ===========================================================================
# Serializers
# ===========================================================================

def _ser_session(s):
    return {
        'id': s.id,
        'campus_id': s.campus_id,
        'class_group_id': s.class_group_id,
        'taken_by_id': str(s.taken_by_id) if s.taken_by_id else None,
        'attendance_date': str(s.attendance_date),
        'session_type': s.session_type,
        'source': s.source,
    }


def _ser_record(r):
    return {
        'id': r.id,
        'student_id': r.student_id,
        'status': r.status,
    }


def _ser_session_report(s):
    return {
        **_ser_session(s),
        'records': [_ser_record(r) for r in s.records.all()],
    }


# ===========================================================================
# Views
# ===========================================================================

@method_decorator(csrf_exempt, name='dispatch')
class CreateSessionView(View):
    """
    POST api/attendance/sessions/create/
    Auth enforced by AttendanceSessionService (attendance.create_session).
    Note: spec says 'manage_attendance' but service enforces 'create_session'.

    Body: {
        class_group_id  : int  (required)
        attendance_date : str  (required, YYYY-MM-DD)
        session_type    : str  (optional, default 'DAILY')
        source          : str  (optional, default 'MANUAL')
    }
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

        class_group_id   = body.get('class_group_id')
        attendance_date  = body.get('attendance_date', '').strip()

        if not class_group_id or not attendance_date:
            return _bad_request('Required: class_group_id, attendance_date')

        try:
            class_group_id = int(class_group_id)
            parsed_date    = date.fromisoformat(attendance_date)
        except (TypeError, ValueError) as e:
            return _bad_request(f'Invalid field value: {e}')

        try:
            session = AttendanceSessionService.create_session(
                person_id=person_id,
                campus_id=campus_id,
                class_group_id=class_group_id,
                attendance_date=parsed_date,
                session_type=body.get('session_type', 'DAILY'),
                source=body.get('source', 'MANUAL'),
            )
            return JsonResponse(_ser_session(session), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class MarkSingleView(View):
    """
    POST api/attendance/sessions/<session_id>/mark/
    Single-record convenience wrapper — delegates to mark_bulk with 1 record.
    Auth enforced by AttendanceMarkingService (attendance.mark_attendance).

    Body: { person_id: int, status: str }
    Note: 'person_id' here is the StudentProfile.id — translated to 'student_id' for the service.
    """
    def post(self, request, session_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        body, err = _parse_body(request)
        if err:
            return err

        student_id = body.get('person_id')
        status     = body.get('status', '').strip().upper()

        if not student_id or not status:
            return _bad_request('Required: person_id, status')

        try:
            student_id = int(student_id)
        except (TypeError, ValueError):
            return _bad_request('person_id must be an integer.')

        try:
            count = AttendanceMarkingService.mark_bulk(
                person_id=person_id,
                campus_id=campus_id,
                session_id=int(session_id),
                attendance_data=[{'student_id': student_id, 'status': status}],
            )
            return JsonResponse({'session_id': int(session_id), 'records_saved': count}, status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class MarkBulkView(View):
    """
    POST api/attendance/sessions/<session_id>/mark-bulk/
    Auth enforced by AttendanceMarkingService (attendance.mark_attendance).

    Body: {
        "records": [
            { "person_id": 1, "status": "PRESENT" },
            { "person_id": 2, "status": "ABSENT" }
        ]
    }
    Note: 'person_id' in body = StudentProfile.id — translated to 'student_id' for the service.
    """
    def post(self, request, session_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        body, err = _parse_body(request)
        if err:
            return err

        records = body.get('records')
        if not records or not isinstance(records, list):
            return _bad_request('Required: records (non-empty list)')

        # Validate and translate each record: person_id → student_id
        translated = []
        for i, rec in enumerate(records):
            sid    = rec.get('person_id')
            status = rec.get('status', '').strip().upper()
            if sid is None or not status:
                return _bad_request(f'Record [{i}]: required fields person_id, status')
            try:
                translated.append({'student_id': int(sid), 'status': status})
            except (TypeError, ValueError):
                return _bad_request(f'Record [{i}]: person_id must be an integer')

        try:
            count = AttendanceMarkingService.mark_bulk(
                person_id=person_id,
                campus_id=campus_id,
                session_id=int(session_id),
                attendance_data=translated,
            )
            return JsonResponse(
                {'session_id': int(session_id), 'records_saved': count},
                status=201,
            )
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class SessionReportView(View):
    """
    GET api/attendance/sessions/<session_id>/report/
    Auth enforced by AttendanceQueryService (attendance.view_attendance).
    Returns session + all attendance records.
    """
    def get(self, request, session_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        try:
            session = AttendanceQueryService.get_session_report(
                person_id=person_id,
                campus_id=campus_id,
                session_id=int(session_id),
            )
            return JsonResponse(_ser_session_report(session))
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class AttendanceSummaryView(View):
    """
    GET api/attendance/summary/
    Auth enforced by AttendanceQueryService (attendance.view_attendance).

    Query params (all required):
        class_group_id : int
        date_from      : YYYY-MM-DD
        date_to        : YYYY-MM-DD
    """
    def get(self, request):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        class_group_id = request.GET.get('class_group_id')
        date_from_raw  = request.GET.get('date_from', '').strip()
        date_to_raw    = request.GET.get('date_to', '').strip()

        if not class_group_id or not date_from_raw or not date_to_raw:
            return _bad_request('Required query params: class_group_id, date_from, date_to')

        try:
            class_group_id = int(class_group_id)
            date_from      = date.fromisoformat(date_from_raw)
            date_to        = date.fromisoformat(date_to_raw)
        except (TypeError, ValueError) as e:
            return _bad_request(f'Invalid param value: {e}')

        if date_from > date_to:
            return _bad_request('date_from must be on or before date_to')

        try:
            summary = AttendanceQueryService.get_summary_by_class_and_date_range(
                person_id=person_id,
                campus_id=campus_id,
                class_group_id=class_group_id,
                date_from=date_from,
                date_to=date_to,
            )
            return JsonResponse({
                'class_group_id': class_group_id,
                'date_from': str(date_from),
                'date_to': str(date_to),
                **summary,
            })
        except Exception as e:
            return _handle_service_error(e)
