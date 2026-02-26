"""
Workforce API Views
Auth: JWT Bearer token → request.person_id (JWTAuthenticationMiddleware)
     Session campus → request.campus_id (CampusContextMiddleware)

All endpoints require valid JWT — no public endpoints.

Pattern (same as all other module APIs):
  1. 401 if request.person_id is None
  2. 400 if request.campus_id is None
  3. Parse JSON body — 400 on malformed
  4. Delegate to service — service handles 403
  5. PermissionDeniedException → 403, ValidationError/BusinessRuleViolation → 400, else → 500

Auth facade: workforce.auth.AuthorizationFacade PREPENDS 'workforce.' automatically.

GAP inventory (4 endpoints):
  GAP-1: GET  devices/          — DeviceRegistrationService.get_devices() not implemented
  GAP-2: POST logs/punch/       — No JWT-gated staff punch method; existing BiometricIngestionService
                                   uses device_token auth, incompatible with this endpoint's device_id body
  GAP-3: GET  logs/             — WorkforceAttendanceQueryService.get_event_log() takes a single
                                   target_person_id with no date range filter
  GAP-4: GET  attendance/summary/ — get_daily_attendance() takes a single date/person;
                                     no campus-wide date-range summary method exists
"""
import json
import logging
from datetime import date, datetime, timezone as dt_timezone

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

from kernel.exceptions import PermissionDeniedException, AuthorizationException, BusinessRuleViolation

from .services.device_service import DeviceRegistrationService
from .services.ingestion_service import BiometricIngestionService, WorkforceIngestionService
from .services.query_service import WorkforceAttendanceQueryService
from .auth import AuthorizationFacade

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


def _gap(endpoint, detail=''):
    logger.warning('GAP: No service method for %s. %s', endpoint, detail)
    return JsonResponse(
        {'error': 'Not implemented', 'gap': endpoint,
         'detail': detail or 'Service method missing. Add to the relevant workforce service.'},
        status=501,
    )


def _handle_service_error(e):
    if isinstance(e, (PermissionDeniedException, AuthorizationException)):
        return JsonResponse({'error': 'Permission denied', 'detail': str(e)}, status=403)
    if isinstance(e, (ValueError, ValidationError, BusinessRuleViolation)):
        return JsonResponse({'error': str(e)}, status=400)
    logger.error('Unexpected error in workforce view', exc_info=e)
    return JsonResponse({'error': 'Internal server error.'}, status=500)


def _parse_body(request):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, _bad_request('Invalid JSON body.')


# ===========================================================================
# Serializers
# ===========================================================================

def _ser_device(d):
    return {
        'id': d.id,
        'campus_id': d.campus_id,
        'name': d.name,
        'device_type': d.device_type,
        'ip_address': d.ip_address,
        'is_active': d.is_active,
    }


def _ser_event(e):
    return {
        'id': e.id,
        'campus_id': e.campus_id,
        'device_id': e.device_id,
        'person_id': str(e.person_id) if e.person_id else None,
        'event_type': e.event_type,
        'event_time': e.event_time.isoformat() if e.event_time else None,
        'source': e.source,
    }


def _ser_daily(d):
    return {
        'id': d.id,
        'campus_id': d.campus_id,
        'person_id': str(d.person_id) if d.person_id else None,
        'date': str(d.date),
        'first_check_in': d.first_check_in.isoformat() if d.first_check_in else None,
        'last_check_out': d.last_check_out.isoformat() if d.last_check_out else None,
    }


# ===========================================================================
# Views — LIVE
# ===========================================================================

@method_decorator(csrf_exempt, name='dispatch')
class DeviceEnrollView(View):
    """
    POST api/workforce/devices/enroll/
    Auth enforced by DeviceRegistrationService (workforce.manage_devices).
    Returns device record + plain_text_token (shown ONCE — not stored in DB).

    Body: {
        name        : str (required)
        device_type : str (required)
        ip_address  : str (optional)
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

        name        = body.get('name', '').strip()
        device_type = body.get('device_type', '').strip()
        if not name or not device_type:
            return _bad_request('Required: name, device_type')

        try:
            device, plain_token = DeviceRegistrationService.register_device(
                person_id=person_id,
                campus_id=campus_id,
                name=name,
                device_type=device_type,
                ip_address=body.get('ip_address'),
            )
            return JsonResponse({
                **_ser_device(device),
                'api_token': plain_token,   # shown once — store securely
                'warning': 'Save this token now. It will not be shown again.',
            }, status=201)
        except Exception as e:
            return _handle_service_error(e)


# ===========================================================================
# Views — GAP (501)
# ===========================================================================

@method_decorator(csrf_exempt, name='dispatch')
class DeviceListView(View):
    """
    GET api/workforce/devices/
    Permission: workforce.manage_devices (enforced here — bare code, facade prepends prefix).
    """
    def get(self, request):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            AuthorizationFacade.require(person_id, campus_id, 'manage_devices')
            devices = DeviceRegistrationService.get_devices(
                campus_id=campus_id,
                person_id=person_id,
            )
            return JsonResponse({
                'count': devices.count(),
                'results': [_ser_device(d) for d in devices],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class PunchLogView(View):
    """
    POST api/workforce/logs/punch/
    Auth enforced by WorkforceIngestionService.staff_punch() (workforce.manage_attendance).
    Body: { device_id, person_id (= target), timestamp, punch_type: IN|OUT }
    punch_type IN → CHECK_IN, OUT → CHECK_OUT.
    """
    PUNCH_MAP = {'IN': 'CHECK_IN', 'OUT': 'CHECK_OUT'}

    def post(self, request):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        body, err = _parse_body(request)
        if err:
            return err

        device_id        = body.get('device_id')
        target_person_id = body.get('person_id')
        timestamp_raw    = body.get('timestamp', '').strip()
        punch_type_raw   = body.get('punch_type', '').strip().upper()

        if not all([device_id, target_person_id, timestamp_raw, punch_type_raw]):
            return _bad_request('Required: device_id, person_id, timestamp, punch_type')

        punch_type = self.PUNCH_MAP.get(punch_type_raw)
        if not punch_type:
            return _bad_request('punch_type must be IN or OUT')

        try:
            device_id        = int(device_id)
            target_person_id = int(target_person_id)
            event_time       = datetime.fromisoformat(timestamp_raw)
        except (TypeError, ValueError) as e:
            return _bad_request(f'Invalid field value: {e}')

        try:
            event = WorkforceIngestionService.staff_punch(
                person_id=person_id,
                campus_id=campus_id,
                device_id=device_id,
                target_person_id=target_person_id,
                punch_type=punch_type,
                event_time=event_time,
            )
            return JsonResponse(_ser_event(event), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class EventLogView(View):
    """
    GET api/workforce/logs/
    Auth enforced by WorkforceAttendanceQueryService.get_event_log_by_range().
    Query params: person_id (optional), date_from (required), date_to (required)
    """
    def get(self, request):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        date_from_raw    = request.GET.get('date_from', '').strip()
        date_to_raw      = request.GET.get('date_to', '').strip()
        target_id_raw    = request.GET.get('person_id')

        if not date_from_raw or not date_to_raw:
            return _bad_request('Required query params: date_from, date_to')

        try:
            date_from        = date.fromisoformat(date_from_raw)
            date_to          = date.fromisoformat(date_to_raw)
            target_person_id = int(target_id_raw) if target_id_raw else None
        except (ValueError, TypeError) as e:
            return _bad_request(f'Invalid param value: {e}')

        if date_from > date_to:
            return _bad_request('date_from must be on or before date_to')

        try:
            events = WorkforceAttendanceQueryService.get_event_log_by_range(
                person_id=person_id,
                campus_id=campus_id,
                date_from=date_from,
                date_to=date_to,
                target_person_id=target_person_id,
            )
            return JsonResponse({
                'count': events.count(),
                'results': [_ser_event(e) for e in events],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class AttendanceSummaryView(View):
    """
    GET api/workforce/attendance/summary/
    Auth enforced by WorkforceAttendanceQueryService.get_summary_by_range().
    Query params: person_id (optional), date_from (required), date_to (required)
    """
    def get(self, request):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()

        date_from_raw    = request.GET.get('date_from', '').strip()
        date_to_raw      = request.GET.get('date_to', '').strip()
        target_id_raw    = request.GET.get('person_id')

        if not date_from_raw or not date_to_raw:
            return _bad_request('Required query params: date_from, date_to')

        try:
            date_from        = date.fromisoformat(date_from_raw)
            date_to          = date.fromisoformat(date_to_raw)
            target_person_id = int(target_id_raw) if target_id_raw else None
        except (ValueError, TypeError) as e:
            return _bad_request(f'Invalid param value: {e}')

        if date_from > date_to:
            return _bad_request('date_from must be on or before date_to')

        try:
            summary = WorkforceAttendanceQueryService.get_summary_by_range(
                person_id=person_id,
                campus_id=campus_id,
                date_from=date_from,
                date_to=date_to,
                target_person_id=target_person_id,
            )
            return JsonResponse(summary)
        except Exception as e:
            return _handle_service_error(e)
