"""
Integration Tests — Auth Flows
Tests for: POST api/auth/login/ (smoke), POST api/auth/set-campus/

Run: pytest tests/integration/test_auth_flows.py -v
"""
import json
from datetime import timedelta
from datetime import datetime, timezone as dt_timezone

import jwt
import pytest
from django.conf import settings
from django.test import TestCase, Client
from django.utils import timezone
from psycopg2.extras import DateTimeTZRange

from kernel.models import (
    Person, Campus, Role, Permission, RolePermissionMap,
    UserRoleBinding, UserAccount,
)


# ===========================================================================
# Helpers (duplicated from test_dashboard_flows for test isolation)
# ===========================================================================

def _make_token(person_id: str) -> str:
    now = datetime.now(tz=dt_timezone.utc)
    payload = {
        'person_id': str(person_id),
        'campus_id': None,
        'iat': now,
        'exp': now + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def _active_validity():
    return DateTimeTZRange(
        lower=timezone.now() - timedelta(hours=1),
        upper=None,
        bounds='[)',
    )


# ===========================================================================
# TestSetCampusView
# ===========================================================================

class TestSetCampusView(TestCase):
    """
    POST api/auth/set-campus/

    Covers:
        test_set_campus_success         → 200, session contains campus_id
        test_set_campus_no_token        → 401
        test_set_campus_invalid_campus  → 404
        test_set_campus_no_binding      → 403 (person has no role at that campus)
    """

    URL = '/api/auth/set-campus/'

    def setUp(self):
        self.client = Client()

        # Campus the person IS bound to
        self.campus = Campus.objects.create(name='SetCampus Test Campus', campus_type='PHYSICAL')

        # A second campus the person has NO binding at
        self.other_campus = Campus.objects.create(name='Unbound Campus', campus_type='PHYSICAL')

        # Person + UserAccount
        self.person = Person.objects.create(
            full_name='Campus Selector',
            primary_phone='+92-3000000001',
        )
        self.user_account = UserAccount.objects.create_user(
            username='campus_selector_test',
            password='securepass123',
            person=self.person,
        )

        # Role (get_or_create because Role.name is unique across the DB)
        self.role, _ = Role.objects.get_or_create(
            name='REGISTRAR',
            defaults={'description': 'Test role', 'is_system_role': True},
        )

        # Active binding at self.campus — NOT at self.other_campus
        self.binding = UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            validity=_active_validity(),
            is_active=True,
        )

        self.token = _make_token(str(self.person.id))
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    # -----------------------------------------------------------------------

    def test_set_campus_success(self):
        """200 — session gains current_campus_id, response confirms it."""
        resp = self.client.post(
            self.URL,
            data=json.dumps({'campus_id': self.campus.id}),
            content_type='application/json',
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, 200, msg=resp.content)

        body = json.loads(resp.content)
        self.assertEqual(body['status'], 'ok')
        self.assertEqual(body['campus_id'], self.campus.id)

        # Session must now contain current_campus_id
        self.assertEqual(
            self.client.session.get('current_campus_id'),
            self.campus.id,
        )

    def test_set_campus_then_dashboard_unblocked(self):
        """
        After set-campus succeeds, a dashboard call that previously returned 400
        should now return something other than 400 (401/403/200 depending on
        what permissions the person has — we just confirm the campus
        400 blocker is gone).
        """
        # Set campus
        self.client.post(
            self.URL,
            data=json.dumps({'campus_id': self.campus.id}),
            content_type='application/json',
            **self.auth_header,
        )

        # Hit dashboard — campus 400 is now resolved
        resp = self.client.get('/api/dashboard/home/', **self.auth_header)
        self.assertNotEqual(
            resp.status_code, 400,
            msg='Dashboard should no longer 400 — campus context is set.',
        )

    def test_set_campus_no_token_returns_401(self):
        """No Authorization header → 401."""
        resp = self.client.post(
            self.URL,
            data=json.dumps({'campus_id': self.campus.id}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)
        body = json.loads(resp.content)
        self.assertIn('error', body)

    def test_set_campus_invalid_campus_returns_404(self):
        """Campus ID that does not exist → 404."""
        resp = self.client.post(
            self.URL,
            data=json.dumps({'campus_id': 999999}),
            content_type='application/json',
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, 404)
        body = json.loads(resp.content)
        self.assertIn('error', body)

    def test_set_campus_no_binding_returns_403(self):
        """
        Campus exists but person has no active UserRoleBinding there → 403.
        Person is bound to self.campus but NOT to self.other_campus.
        """
        resp = self.client.post(
            self.URL,
            data=json.dumps({'campus_id': self.other_campus.id}),
            content_type='application/json',
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, 403)
        body = json.loads(resp.content)
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Forbidden')

    def test_set_campus_missing_campus_id_returns_400(self):
        """Empty body / missing campus_id → 400."""
        resp = self.client.post(
            self.URL,
            data=json.dumps({}),
            content_type='application/json',
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, 400)

    def test_set_campus_noncallable_campus_id_returns_400(self):
        """Non-integer campus_id → 400."""
        resp = self.client.post(
            self.URL,
            data=json.dumps({'campus_id': 'not_an_int'}),
            content_type='application/json',
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, 400)

    def test_set_campus_expired_binding_returns_403(self):
        """
        An expired UserRoleBinding (validity range ended yesterday) → 403.
        The person has no currently-valid role at the campus.
        """
        # Override existing binding validity to be expired
        self.binding.validity = DateTimeTZRange(
            lower=timezone.now() - timedelta(days=10),
            upper=timezone.now() - timedelta(days=1),  # ended yesterday
            bounds='[)',
        )
        self.binding.is_active = False
        self.binding.save()

        resp = self.client.post(
            self.URL,
            data=json.dumps({'campus_id': self.campus.id}),
            content_type='application/json',
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, 403)

    def test_get_method_not_allowed(self):
        """GET on a POST-only endpoint → 405."""
        resp = self.client.get(self.URL, **self.auth_header)
        self.assertEqual(resp.status_code, 405)
