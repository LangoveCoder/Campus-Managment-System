"""
Integration Test Suite — Dashboard API Flows

Tests the full system chain:
  JWT middleware → CampusContextMiddleware → AuthorizationFacade
  → AuthorizationService → module query service → database → JSON response

No mocking. Real database. Real auth. Real permission checks.

Flows:
  Flow 1 — No token                     → 401 on all 3 endpoints
  Flow 2 — Malformed Bearer token       → 401 on all 3 endpoints
  Flow 3 — Valid token, no campus       → 400 on all 3 endpoints
  Flow 4 — Valid token, wrong perm      → 403 on all 3 endpoints
  Flow 5 — Full happy path              → 200, correct keys, correct counts

Run: pytest tests/integration/test_dashboard_flows.py -v
"""
import json
from datetime import date, datetime, timedelta, timezone as dt_timezone
from decimal import Decimal

import jwt
import pytest
from django.conf import settings
from django.test import TestCase, Client
from django.utils import timezone
from psycopg2.extras import DateTimeTZRange

# --- Kernel models ----------------------------------------------------------
from kernel.models import (
    Person, Campus, Role, Permission, RolePermissionMap,
    UserRoleBinding, UserAccount,
)

# --- Academic models --------------------------------------------------------
from modules.academics.models.academic_program import AcademicProgram
from modules.academics.models.assessment_scheme import AssessmentScheme
from modules.academics.models.academic_cycle import AcademicCycle
from modules.academics.models.class_group import ClassGroup
from modules.academics.models.course import Course
from modules.academics.models.course_offering import CourseOffering
from modules.academics.models.student_profile import StudentProfile
from modules.academics.models.enrollment import Enrollment
from modules.academics.models.assessment_period import AssessmentPeriod
from modules.academics.models.assessment_instance import AssessmentInstance
from modules.academics.models.assessment_result import AssessmentResult

# --- Attendance models ------------------------------------------------------
from modules.attendance.models.ledger import AttendanceSession, AttendanceRecord


# ===========================================================================
# Helpers
# ===========================================================================

def _make_token(person_id: str) -> str:
    """Generate a valid 24-hour JWT for the given person UUID string."""
    now = datetime.now(tz=dt_timezone.utc)
    payload = {
        'person_id': str(person_id),
        'campus_id': None,
        'iat': now,
        'exp': now + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def _auth_header(token: str) -> dict:
    return {'HTTP_AUTHORIZATION': f'Bearer {token}'}


def _set_campus_in_session(client: Client, campus_id: int) -> None:
    """Inject campus into the client session, mimicking the campus picker flow."""
    session = client.session
    session['current_campus_id'] = campus_id
    session.save()


def _assert_all_return(responses: list, expected_status: int, test_case: TestCase) -> None:
    for i, resp in enumerate(responses):
        test_case.assertEqual(
            resp.status_code,
            expected_status,
            msg=f"Endpoint #{i + 1} returned {resp.status_code}, expected {expected_status}. "
                f"Body: {resp.content[:200]}",
        )


# ===========================================================================
# World Builder — creates a complete test universe in the DB
# ===========================================================================

class TestWorld:
    """
    Builds a fully wired test world programmatically.

    Caller controls which permissions are granted to the test person,
    allowing Flow 4 to omit dashboard permissions.
    """

    def __init__(self, campus_name: str = 'Test Campus Alpha', grant_dashboard_perms: bool = True):
        self.campus = Campus.objects.create(name=campus_name, campus_type='PHYSICAL')

        # --- Identity -------------------------------------------------------
        self.person = Person.objects.create(
            full_name='Test Admin User',
            primary_phone=f'+92-3001234567',
        )
        self.user_account = UserAccount.objects.create_user(
            username=f'testadmin_{campus_name[:5].replace(" ", "")}',
            password='testpass_secure_123',
            person=self.person,
        )

        # --- Role + Permissions ---------------------------------------------
        self.role, _ = Role.objects.get_or_create(
            name='CAMPUS_ADMIN',
            defaults={'description': 'Campus Administration', 'is_system_role': True},
        )

        if grant_dashboard_perms:
            self._grant_permission('academics.view_program',      'View Program',         'academics')
            self._grant_permission('attendance.view_attendance',   'View Attendance',      'attendance')
            self._grant_permission('academics.view_student_results', 'View Results',       'academics')

        # --- Bind person to role at campus ----------------------------------
        self.binding = UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            validity=DateTimeTZRange(
                lower=timezone.now() - timedelta(hours=1),
                upper=None,     # open-ended: never expires
                bounds='[)',
            ),
            is_active=True,
        )

        self.token = _make_token(str(self.person.id))

    def _grant_permission(self, code: str, name: str, module: str) -> None:
        perm, _ = Permission.objects.get_or_create(
            code=code,
            defaults={'name': name, 'module': module},
        )
        RolePermissionMap.objects.get_or_create(
            role=self.role,
            permission=perm,
            defaults={'granted_by': None},
        )


class AcademicWorld:
    """
    Builds the academic and attendance data on top of a TestWorld.
    Required only for Flow 5 (happy path).
    """

    def __init__(self, world: TestWorld):
        self.campus = world.campus
        self.admin_person = world.person

        # --- Assessment scheme (program needs one) -------------------------
        self.scheme = AssessmentScheme.objects.create(
            campus=self.campus,
            name='Standard Scheme',
        )

        # --- Program → Cycle → ClassGroup -----------------------------------
        self.program = AcademicProgram.objects.create(
            campus=self.campus,
            name='Secondary Education Program',
            code='SEP-001',
            program_type='SECONDARY',
            assessment_scheme=self.scheme,
        )
        self.cycle = AcademicCycle.objects.create(
            campus=self.campus,
            academic_program=self.program,
            name='Year One',
            sequence=1,
            start_date=date(2026, 1, 1),
            end_date=None,          # open-ended — active indefinitely
            is_active=True,
        )
        self.class_group = ClassGroup.objects.create(
            campus=self.campus,
            academic_cycle=self.cycle,
            name='Grade 7',
            section='Blue',
            is_active=True,
        )

        # --- Course + Offering ----------------------------------------------
        self.course = Course.objects.create(
            campus=self.campus,
            name='Mathematics',
            code='MATH-101',
        )
        self.offering = CourseOffering.objects.create(
            campus=self.campus,
            course=self.course,
            academic_program=self.program,
        )

        # --- Assessment chain -----------------------------------------------
        self.period = AssessmentPeriod.objects.create(
            assessment_scheme=self.scheme,
            name='Mid-Term',
            sequence=1,
        )
        self.assessment_instance = AssessmentInstance.objects.create(
            campus=self.campus,
            class_group=self.class_group,
            assessment_period=self.period,
            course_offering=self.offering,
            max_marks=Decimal('100.00'),
            scheduled_date=date(2026, 1, 20),
        )

        # --- Two student persons + profiles + enrollments -------------------
        self.students = []
        self.enrollments = []
        for i in range(2):
            sp = Person.objects.create(
                full_name=f'Student {i + 1}',
                primary_phone=f'+92-30099999{i:02d}',
            )
            profile = StudentProfile.objects.create(
                campus=self.campus,
                person=sp,
                academic_program=self.program,
                admission_number=f'ADM-2026-{i + 1:04d}',
                admission_date=date(2026, 1, 1),
                status='ACTIVE',
            )
            enrollment = Enrollment.objects.create(
                campus=self.campus,
                student_profile=profile,
                class_group=self.class_group,
                enrollment_date=date(2026, 1, 1),
                status='ACTIVE',
            )
            self.students.append(profile)
            self.enrollments.append(enrollment)

        # --- One attendance session with both students PRESENT --------------
        self.session = AttendanceSession.objects.create(
            campus=self.campus,
            class_group=self.class_group,
            taken_by=self.admin_person,
            attendance_date=date(2026, 2, 1),
            session_type='DAILY',
            source='MANUAL',
        )
        for profile in self.students:
            AttendanceRecord.objects.create(
                campus=self.campus,
                session=self.session,
                student=profile,
                status='PRESENT',
            )

        # --- Assessment results: 70, 80, 90 (3rd enrollment faked below) ---
        # Add a third student so we can test avg/high/low properly
        sp3 = Person.objects.create(
            full_name='Student 3',
            primary_phone='+92-3009999902',
        )
        self.profile3 = StudentProfile.objects.create(
            campus=self.campus,
            person=sp3,
            academic_program=self.program,
            admission_number='ADM-2026-0003',
            admission_date=date(2026, 1, 1),
            status='ACTIVE',
        )
        self.enrollment3 = Enrollment.objects.create(
            campus=self.campus,
            student_profile=self.profile3,
            class_group=self.class_group,
            enrollment_date=date(2026, 1, 1),
            status='ACTIVE',
        )

        for enrollment, marks in zip(
            [self.enrollments[0], self.enrollments[1], self.enrollment3],
            [Decimal('70.00'), Decimal('80.00'), Decimal('90.00')],
        ):
            AssessmentResult.objects.create(
                campus=self.campus,
                enrollment=enrollment,
                assessment_instance=self.assessment_instance,
                marks_obtained=marks,
                is_absent=False,
                entered_by=self.admin_person,
            )


# ===========================================================================
# Flow 1 — Unauthenticated: no Authorization header
# ===========================================================================

class TestFlow1Unauthenticated(TestCase):
    """No token → 401 on all three endpoints."""

    ENDPOINTS = [
        '/api/dashboard/home/',
        '/api/dashboard/attendance/?class_group_id=1&date_from=2026-01-01&date_to=2026-02-28',
        '/api/dashboard/assessments/?class_group_id=1&assessment_instance_id=1',
    ]

    def setUp(self):
        self.client = Client()

    def test_no_token_returns_401_on_all_endpoints(self):
        responses = [self.client.get(ep) for ep in self.ENDPOINTS]
        _assert_all_return(responses, 401, self)

    def test_response_body_contains_error_field(self):
        resp = self.client.get('/api/dashboard/home/')
        self.assertEqual(resp.status_code, 401)
        body = json.loads(resp.content)
        self.assertIn('error', body)


# ===========================================================================
# Flow 2 — Invalid token (malformed Bearer)
# ===========================================================================

class TestFlow2InvalidToken(TestCase):
    """Malformed / expired / bad-signature token → 401 on all three."""

    ENDPOINTS = [
        '/api/dashboard/home/',
        '/api/dashboard/attendance/?class_group_id=1&date_from=2026-01-01&date_to=2026-02-28',
        '/api/dashboard/assessments/?class_group_id=1&assessment_instance_id=1',
    ]

    def setUp(self):
        self.client = Client()

    def _hit(self, token: str):
        headers = _auth_header(token)
        return [self.client.get(ep, **headers) for ep in self.ENDPOINTS]

    def test_malformed_string_returns_401(self):
        responses = self._hit('this.is.not.a.jwt')
        _assert_all_return(responses, 401, self)

    def test_empty_bearer_returns_401(self):
        responses = self._hit('')
        _assert_all_return(responses, 401, self)

    def test_expired_token_returns_401(self):
        now = datetime.now(tz=dt_timezone.utc)
        payload = {
            'person_id': '00000000-0000-0000-0000-000000000001',
            'campus_id': None,
            'iat': now - timedelta(hours=48),
            'exp': now - timedelta(hours=24),   # expired yesterday
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        responses = self._hit(token)
        _assert_all_return(responses, 401, self)

    def test_wrong_secret_returns_401(self):
        now = datetime.now(tz=dt_timezone.utc)
        payload = {
            'person_id': '00000000-0000-0000-0000-000000000001',
            'campus_id': None,
            'iat': now,
            'exp': now + timedelta(hours=24),
        }
        token = jwt.encode(payload, 'WRONG_SECRET_KEY', algorithm='HS256')
        responses = self._hit(token)
        _assert_all_return(responses, 401, self)

    def test_valid_signature_nonexistent_person_returns_401(self):
        """Token is cryptographically valid but person UUID does not exist in DB."""
        now = datetime.now(tz=dt_timezone.utc)
        payload = {
            'person_id': '00000000-dead-beef-0000-000000000000',
            'campus_id': None,
            'iat': now,
            'exp': now + timedelta(hours=24),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        responses = self._hit(token)
        _assert_all_return(responses, 401, self)


# ===========================================================================
# Flow 3 — Valid token, no campus context
# ===========================================================================

class TestFlow3ValidTokenNoCampus(TestCase):
    """Valid token but no campus in session → 400 on all three."""

    def setUp(self):
        self.client = Client()
        self.world = TestWorld(campus_name='Flow3 Campus')
        self.headers = _auth_header(self.world.token)

    def test_no_campus_returns_400_on_all_endpoints(self):
        # Deliberately NOT calling _set_campus_in_session
        responses = [
            self.client.get('/api/dashboard/home/', **self.headers),
            self.client.get(
                '/api/dashboard/attendance/?class_group_id=1&date_from=2026-01-01&date_to=2026-02-28',
                **self.headers,
            ),
            self.client.get(
                '/api/dashboard/assessments/?class_group_id=1&assessment_instance_id=1',
                **self.headers,
            ),
        ]
        _assert_all_return(responses, 400, self)

    def test_no_campus_body_mentions_campus(self):
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        body = json.loads(resp.content)
        self.assertIn('error', body)
        self.assertIn('campus', body['error'].lower())


# ===========================================================================
# Flow 4 — Valid token, valid campus, wrong permission
# ===========================================================================

class TestFlow4WrongPermission(TestCase):
    """Person has a valid binding but role grants NO dashboard permissions → 403."""

    def setUp(self):
        self.client = Client()
        # grant_dashboard_perms=False → role exists but no permissions mapped
        self.world = TestWorld(campus_name='Flow4 Campus', grant_dashboard_perms=False)
        self.acadworld = AcademicWorld(self.world)
        self.headers = _auth_header(self.world.token)
        _set_campus_in_session(self.client, self.world.campus.id)

    def test_wrong_permission_home_returns_403(self):
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        self.assertEqual(resp.status_code, 403)

    def test_wrong_permission_attendance_returns_403(self):
        resp = self.client.get(
            f'/api/dashboard/attendance/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&date_from=2026-01-01&date_to=2026-02-28',
            **self.headers,
        )
        self.assertEqual(resp.status_code, 403)

    def test_wrong_permission_assessments_returns_403(self):
        resp = self.client.get(
            f'/api/dashboard/assessments/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&assessment_instance_id={self.acadworld.assessment_instance.id}',
            **self.headers,
        )
        self.assertEqual(resp.status_code, 403)

    def test_403_response_has_error_field(self):
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        body = json.loads(resp.content)
        self.assertIn('error', body)


# ===========================================================================
# Flow 5 — Full happy path
# ===========================================================================

class TestFlow5HappyPath(TestCase):
    """
    Complete chain: login → token → campus context → permission check → data.
    Asserts HTTP 200, correct keys, mathematically correct counts.
    """

    def setUp(self):
        self.client = Client()
        self.world = TestWorld(campus_name='Flow5 Campus', grant_dashboard_perms=True)
        self.acadworld = AcademicWorld(self.world)
        self.headers = _auth_header(self.world.token)
        _set_campus_in_session(self.client, self.world.campus.id)

    # -----------------------------------------------------------------------
    # Home endpoint
    # -----------------------------------------------------------------------

    def test_home_returns_200(self):
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        self.assertEqual(resp.status_code, 200, msg=resp.content)

    def test_home_response_has_required_keys(self):
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        body = json.loads(resp.content)
        self.assertIn('campus', body)
        self.assertIn('active_persons_at_campus', body)
        self.assertIn('total_students_enrolled', body)
        self.assertIn('total_active_class_groups', body)

    def test_home_campus_id_and_name_are_correct(self):
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        body = json.loads(resp.content)
        self.assertEqual(body['campus']['name'], 'Flow5 Campus')
        self.assertEqual(body['campus']['id'], self.world.campus.id)

    def test_home_total_students_enrolled_is_correct(self):
        """3 students enrolled (ACTIVE) in the class group."""
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        body = json.loads(resp.content)
        self.assertEqual(body['total_students_enrolled'], 3)

    def test_home_total_active_class_groups_is_correct(self):
        """1 class group in an active cycle (end_date=None)."""
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        body = json.loads(resp.content)
        self.assertEqual(body['total_active_class_groups'], 1)

    def test_home_active_persons_at_campus_includes_admin(self):
        """The admin person has an active, currently valid binding."""
        resp = self.client.get('/api/dashboard/home/', **self.headers)
        body = json.loads(resp.content)
        self.assertGreaterEqual(body['active_persons_at_campus'], 1)

    # -----------------------------------------------------------------------
    # Attendance endpoint
    # -----------------------------------------------------------------------

    def test_attendance_returns_200(self):
        url = (
            f'/api/dashboard/attendance/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&date_from=2026-01-01&date_to=2026-02-28'
        )
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200, msg=resp.content)

    def test_attendance_response_has_required_keys(self):
        url = (
            f'/api/dashboard/attendance/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&date_from=2026-01-01&date_to=2026-02-28'
        )
        resp = self.client.get(url, **self.headers)
        body = json.loads(resp.content)
        for key in ('total_sessions', 'present', 'absent', 'late', 'excused'):
            self.assertIn(key, body, msg=f"Key '{key}' missing from response")

    def test_attendance_counts_are_mathematically_correct(self):
        """1 session created, 2 students both PRESENT, 0 absent."""
        url = (
            f'/api/dashboard/attendance/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&date_from=2026-01-01&date_to=2026-02-28'
        )
        resp = self.client.get(url, **self.headers)
        body = json.loads(resp.content)
        self.assertEqual(body['total_sessions'], 1)
        self.assertEqual(body['present'], 2)
        self.assertEqual(body['absent'], 0)
        self.assertEqual(body['late'], 0)
        self.assertEqual(body['excused'], 0)

    def test_attendance_missing_params_returns_400(self):
        resp = self.client.get('/api/dashboard/attendance/', **self.headers)
        self.assertEqual(resp.status_code, 400)

    def test_attendance_returns_empty_for_out_of_range_dates(self):
        """Date range that doesn't include the session date → 0 sessions, 0 records."""
        url = (
            f'/api/dashboard/attendance/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&date_from=2025-01-01&date_to=2025-12-31'
        )
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content)
        self.assertEqual(body['total_sessions'], 0)
        self.assertEqual(body['present'], 0)

    # -----------------------------------------------------------------------
    # Assessment endpoint
    # -----------------------------------------------------------------------

    def test_assessments_returns_200(self):
        url = (
            f'/api/dashboard/assessments/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&assessment_instance_id={self.acadworld.assessment_instance.id}'
        )
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200, msg=resp.content)

    def test_assessments_response_has_required_keys(self):
        url = (
            f'/api/dashboard/assessments/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&assessment_instance_id={self.acadworld.assessment_instance.id}'
        )
        resp = self.client.get(url, **self.headers)
        body = json.loads(resp.content)
        for key in ('average', 'highest', 'lowest', 'total_results', 'absent_count'):
            self.assertIn(key, body, msg=f"Key '{key}' missing from response")

    def test_assessments_statistics_are_mathematically_correct(self):
        """
        Marks entered: 70, 80, 90
        Expected: average=80.0, highest=90.0, lowest=70.0, total_results=3
        """
        url = (
            f'/api/dashboard/assessments/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&assessment_instance_id={self.acadworld.assessment_instance.id}'
        )
        resp = self.client.get(url, **self.headers)
        body = json.loads(resp.content)
        self.assertEqual(body['total_results'], 3)
        self.assertAlmostEqual(body['average'], 80.0, places=2)
        self.assertAlmostEqual(body['highest'], 90.0, places=2)
        self.assertAlmostEqual(body['lowest'],  70.0, places=2)
        self.assertEqual(body['absent_count'], 0)

    def test_assessments_missing_params_returns_400(self):
        resp = self.client.get('/api/dashboard/assessments/', **self.headers)
        self.assertEqual(resp.status_code, 400)

    def test_assessments_empty_for_nonexistent_instance(self):
        """Assessment instance ID that doesn't exist → 200 with zero counts."""
        url = (
            f'/api/dashboard/assessments/'
            f'?class_group_id={self.acadworld.class_group.id}'
            f'&assessment_instance_id=999999'
        )
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content)
        self.assertEqual(body['total_results'], 0)
        self.assertIsNone(body['average'])


# ===========================================================================
# Flow 5b — Login endpoint (POST api/auth/login/)
# ===========================================================================

class TestLoginEndpoint(TestCase):
    """Tests for the JWT login view directly."""

    def setUp(self):
        self.client = Client()
        self.world = TestWorld(campus_name='Login Test Campus')

    def test_valid_credentials_return_200_with_token(self):
        resp = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': self.world.user_account.username, 'password': 'testpass_secure_123'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200, msg=resp.content)
        body = json.loads(resp.content)
        self.assertIn('access_token', body)
        self.assertIn('person_id', body)
        self.assertIn('name', body)

    def test_returned_token_is_valid_jwt(self):
        resp = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': self.world.user_account.username, 'password': 'testpass_secure_123'}),
            content_type='application/json',
        )
        body = json.loads(resp.content)
        token = body['access_token']
        # Decode without verification first to check structure
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        self.assertIn('person_id', payload)
        self.assertIn('exp', payload)

    def test_returned_name_matches_person_full_name(self):
        resp = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': self.world.user_account.username, 'password': 'testpass_secure_123'}),
            content_type='application/json',
        )
        body = json.loads(resp.content)
        self.assertEqual(body['name'], 'Test Admin User')

    def test_wrong_password_returns_401(self):
        resp = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': self.world.user_account.username, 'password': 'wrongpassword'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)
        body = json.loads(resp.content)
        self.assertIn('error', body)

    def test_unknown_username_returns_401(self):
        resp = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'nobody_here', 'password': 'anything'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_missing_fields_returns_400(self):
        resp = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'only_username_no_password'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_get_method_not_allowed(self):
        resp = self.client.get('/api/auth/login/')
        self.assertEqual(resp.status_code, 405)
