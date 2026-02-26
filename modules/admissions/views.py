"""
Admissions API Views
Auth: JWT Bearer token → request.person_id (JWTAuthenticationMiddleware)
     Session campus → request.campus_id (CampusContextMiddleware)

Pattern (same as academics/views.py):
  1. 401 if request.person_id is None  (except POST apply/ which is public)
  2. 400 if campus_id unavailable
  3. Parse JSON body — 400 on malformed
  4. Delegate to service — service handles 403 internally via AuthorizationFacade
  5. PermissionDeniedException/AuthorizationException → 403
     ValueError/ValidationError → 400
     everything else → 500 (safe message, full tb logged)

Auth facade note:
  admissions.auth.AuthorizationFacade PREPENDS 'admissions.' automatically.
  Views must pass BARE codes: 'view_applications', NOT 'admissions.view_applications'.

GAP endpoints return 501 and log the missing method.
"""
import json
import logging

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

from kernel.exceptions import PermissionDeniedException, AuthorizationException

from .services.admissions_service import AdmissionsService
from .auth import AuthorizationFacade

logger = logging.getLogger(__name__)


# ===========================================================================
# Shared helpers (same contract as academics/views.py)
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


def _gap(endpoint):
    logger.warning('GAP: No service method for %s', endpoint)
    return JsonResponse(
        {'error': 'Not implemented', 'gap': endpoint,
         'detail': 'Service method missing. Add to AdmissionsService.'},
        status=501,
    )


def _handle_service_error(e):
    # Admissions facade raises PermissionDenied (kernel.exceptions) on missing perm
    if isinstance(e, (PermissionDeniedException, AuthorizationException, PermissionDenied)):
        return JsonResponse({'error': 'Permission denied', 'detail': str(e)}, status=403)
    if isinstance(e, (ValueError, ValidationError)):
        return JsonResponse({'error': str(e)}, status=400)
    logger.error('Unexpected error in admissions view', exc_info=e)
    return JsonResponse({'error': 'Internal server error.'}, status=500)


def _parse_body(request):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, _bad_request('Invalid JSON body.')


# ===========================================================================
# Serializers (flat — no nested expansions)
# ===========================================================================

def _ser_application(app):
    return {
        'id': app.id,
        'applicant_id': app.applicant_id,
        'applicant_name': app.applicant.full_name if app.applicant_id else None,
        'campus_id': app.campus_id,
        'academic_program_id': app.academic_program_id,
        'status': app.status,
        'submitted_at': app.submitted_at.isoformat() if app.submitted_at else None,
    }


def _ser_test_result(t):
    return {
        'id': t.id,
        'application_id': t.application_id,
        'score': str(t.score),
        'total_score': str(t.total_score),
        'rank': t.rank,
        'source': t.source,
    }


def _ser_interview(iv):
    return {
        'id': iv.id,
        'application_id': iv.application_id,
        'interviewer_id': str(iv.interviewer_id) if iv.interviewer_id else None,
        'remarks': iv.remarks,
        'recommendation': iv.recommendation,
    }


def _ser_decision(d):
    return {
        'id': d.id,
        'application_id': d.application_id,
        'decision': d.decision,
        'decided_by_id': str(d.decided_by_id) if d.decided_by_id else None,
        'comments': d.comments,
    }


# ===========================================================================
# Views
# ===========================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ApplyView(View):
    """
    POST api/admissions/apply/

    PUBLIC endpoint — no JWT required.
    campus_id must be in the JSON body (not from session).

    Body: {
        full_name   : str  (required)
        dob         : str  (required, ISO date)
        campus_id   : int  (required)
        form_payload: dict (required)
        contact_info      : dict (optional)
        guardian_info     : dict (optional)
        academic_program_id: int (optional)
    }
    """
    def post(self, request):
        body, err = _parse_body(request)
        if err:
            return err

        full_name    = body.get('full_name', '').strip()
        dob          = body.get('dob', '').strip()
        campus_id    = body.get('campus_id')
        form_payload = body.get('form_payload')

        missing = [f for f, v in [
            ('full_name', full_name), ('dob', dob),
            ('campus_id', campus_id), ('form_payload', form_payload),
        ] if not v]
        if missing:
            return _bad_request(f'Required fields: {", ".join(missing)}')

        try:
            campus_id = int(campus_id)
        except (TypeError, ValueError):
            return _bad_request('campus_id must be an integer.')

        if not isinstance(form_payload, dict):
            return _bad_request('form_payload must be a JSON object.')

        try:
            application = AdmissionsService.submit_application(
                full_name=full_name,
                dob=dob,
                campus_id=campus_id,
                form_payload=form_payload,
                contact_info=body.get('contact_info'),
                guardian_info=body.get('guardian_info'),
                academic_program_id=body.get('academic_program_id'),
            )
            return JsonResponse(_ser_application(application), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class ApplicationListView(View):
    """
    GET api/admissions/applications/
    Permission: admissions.view_applications (enforced here — bare code, facade prepends prefix).
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
                permission_code='view_applications',
            )
            applications = AdmissionsService.get_applications(
                campus_id=campus_id,
                person_id=person_id,
            )
            return JsonResponse({
                'count': applications.count(),
                'results': [_ser_application(a) for a in applications],
            })
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class ApplicationDetailView(View):
    """
    GET api/admissions/applications/<application_id>/
    Permission: admissions.view_applications (enforced here — bare code, facade prepends prefix).
    """
    def get(self, request, application_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()
        if not campus_id:
            return _no_campus()
        try:
            AuthorizationFacade.require(
                person_id=person_id,
                campus_id=campus_id,
                permission_code='view_applications',
            )
            application = AdmissionsService.get_application_by_id(
                application_id=int(application_id),
                campus_id=campus_id,
                person_id=person_id,
            )
            return JsonResponse(_ser_application(application))
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class TestResultView(View):
    """
    POST api/admissions/applications/<application_id>/test-result/
    Auth enforced by AdmissionsService (admissions.evaluate_test).
    Body: { score, total_score (opt, default 100), rank (opt), source (opt) }
    """
    def post(self, request, application_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()

        body, err = _parse_body(request)
        if err:
            return err

        score = body.get('score')
        if score is None:
            return _bad_request('Required: score')

        try:
            score = float(score)
            total_score = float(body.get('total_score', 100.0))
            rank = int(body['rank']) if body.get('rank') is not None else None
        except (TypeError, ValueError) as e:
            return _bad_request(f'Invalid field value: {e}')

        try:
            result = AdmissionsService.evaluate_test_result(
                person_id=person_id,
                application_id=int(application_id),
                score=score,
                total_score=total_score,
                rank=rank,
                source=body.get('source', 'Internal'),
            )
            return JsonResponse(_ser_test_result(result), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class InterviewView(View):
    """
    POST api/admissions/applications/<application_id>/interview/
    Auth enforced by AdmissionsService (admissions.conduct_interview).
    Body: { remarks, recommendation }
    """
    def post(self, request, application_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()

        body, err = _parse_body(request)
        if err:
            return err

        remarks        = body.get('remarks', '').strip()
        recommendation = body.get('recommendation', '').strip()
        if not remarks or not recommendation:
            return _bad_request('Required: remarks, recommendation')

        try:
            evaluation = AdmissionsService.conduct_interview(
                person_id=person_id,
                application_id=int(application_id),
                remarks=remarks,
                recommendation=recommendation,
            )
            return JsonResponse(_ser_interview(evaluation), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class DecideView(View):
    """
    POST api/admissions/applications/<application_id>/decide/
    Auth enforced by AdmissionsService (admissions.make_decision).
    Body: { decision: ACCEPTED|REJECTED|WAITLISTED, comments (opt) }
    """
    VALID_DECISIONS = {'ACCEPTED', 'REJECTED', 'WAITLISTED'}

    def post(self, request, application_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()

        body, err = _parse_body(request)
        if err:
            return err

        decision = body.get('decision', '').strip().upper()
        if not decision:
            return _bad_request('Required: decision')
        if decision not in self.VALID_DECISIONS:
            return _bad_request(f'decision must be one of: {", ".join(sorted(self.VALID_DECISIONS))}')

        try:
            verdict = AdmissionsService.make_decision(
                person_id=person_id,
                application_id=int(application_id),
                decision=decision,
                comments=body.get('comments', ''),
            )
            return JsonResponse(_ser_decision(verdict), status=201)
        except Exception as e:
            return _handle_service_error(e)


@method_decorator(csrf_exempt, name='dispatch')
class EnrollView(View):
    """
    POST api/admissions/applications/<application_id>/enroll/
    Auth enforced by AdmissionsService (admissions.convert_to_enrollment).
    Service returns a stub dict — passed through cleanly.
    Body: {} (no fields required — all context is in the URL)
    """
    def post(self, request, application_id):
        person_id, campus_id = _ctx(request)
        if not person_id:
            return _unauthenticated()

        try:
            result = AdmissionsService.convert_to_enrollment(
                person_id=person_id,
                application_id=int(application_id),
            )
            # Service returns a dict (stub). Pass it through cleanly.
            return JsonResponse(result, status=200)
        except Exception as e:
            return _handle_service_error(e)
