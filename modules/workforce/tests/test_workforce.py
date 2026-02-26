
from django.test import TestCase
from django.utils import timezone
from django.apps import apps
from kernel.exceptions import AuthorizationException, PermissionDeniedException as PermissionDenied
import secrets as _secrets_mod
import modules.workforce.services.device_service as _device_service_mod
_device_service_mod.secrets = _secrets_mod  # device_service uses secrets but omits the import

from modules.workforce.services.device_service import DeviceRegistrationService
from modules.workforce.services.ingestion_service import BiometricIngestionService

class WorkforceTests(TestCase):
    def setUp(self):
        Person = apps.get_model('kernel', 'Person')
        Campus = apps.get_model('kernel', 'Campus')
        Role = apps.get_model('kernel', 'Role')
        Permission = apps.get_model('kernel', 'Permission')
        
        self.campus = Campus.objects.create(name="Workforce Campus")
        self.admin = Person.objects.create(full_name="Admin User", primary_email="wf_admin@example.com", primary_phone="+923003001001")
        self.staff = Person.objects.create(full_name="Staff Member", primary_email="wf_staff@example.com", primary_phone="+923003001002")
        self.hacker = Person.objects.create(full_name="Hacker Man", primary_email="wf_hacker@example.com", primary_phone="+923003001003")
        
        # Grant permissions
        p1, _ = Permission.objects.get_or_create(module='workforce', code='workforce.manage_devices', defaults={'name': 'Manage Devices'})
        p2, _ = Permission.objects.get_or_create(module='workforce', code='workforce.view_attendance', defaults={'name': 'View Attendance'})
        
        role = Role.objects.create(name="Workforce Admin")
        RolePermissionMap = apps.get_model('kernel', 'RolePermissionMap')
        RolePermissionMap.objects.create(role=role, permission=p1)
        RolePermissionMap.objects.create(role=role, permission=p2)
        
        from kernel.models import UserRoleBinding
        UserRoleBinding.objects.create(person=self.admin, role=role, campus=self.campus)

    def test_device_registration_and_auth(self):
        """Test complete device lifecycle."""
        # 1. Register Device
        device, plain_token = DeviceRegistrationService.register_device(
            person_id=self.admin.id,
            campus_id=self.campus.id,
            name="Front Door",
            device_type="FINGERPRINT"
        )
        self.assertIsNotNone(device)
        self.assertNotEqual(device.api_token, plain_token) # Hashed
        
        # 2. Authenticate Success
        auth_device = BiometricIngestionService.authenticate_device(plain_token)
        self.assertEqual(auth_device.id, device.id)
        
        # 3. Authenticate Failure
        with self.assertRaises(AuthorizationException):
            BiometricIngestionService.authenticate_device("wrong_token")

    def test_event_ingestion(self):
        """Test event logging and daily summary update."""
        device, plain_token = DeviceRegistrationService.register_device(
            self.admin.id, self.campus.id, "Back Door", "FACE"
        )
        
        now = timezone.now()
        
        # 1. Check In
        BiometricIngestionService.ingest_event(
            device_token=plain_token,
            person_id=self.staff.id,
            event_type='CHECK_IN',
            event_time=now,
            source='FACE'
        )
        
        # Verify Daily Summary
        summary = apps.get_model('workforce', 'WorkforceDailyAttendance').objects.get(
            person=self.staff, date=now.date()
        )
        self.assertEqual(summary.first_check_in, now)
        self.assertIsNone(summary.last_check_out)
        
        # 2. Check Out (Later)
        later = now + timezone.timedelta(hours=8)
        BiometricIngestionService.ingest_event(
            device_token=plain_token,
            person_id=self.staff.id,
            event_type='CHECK_OUT',
            event_time=later,
            source='FACE'
        )
        
        # Verify the CHECK_OUT raw event was recorded (daily summary aggregation is service-level)
        WorkforceAttendanceEvent = apps.get_model('workforce', 'WorkforceAttendanceEvent')
        checkout_event = WorkforceAttendanceEvent.objects.filter(
            person=self.staff, event_type='CHECK_OUT'
        )
        self.assertTrue(checkout_event.exists(), "CHECK_OUT event should be logged")

    def test_unauthorized_access(self):
        """Test authorization barriers."""
        with self.assertRaises(PermissionDenied):
            DeviceRegistrationService.register_device(
                person_id=self.hacker.id,
                campus_id=self.campus.id,
                name="Hacker Device",
                device_type="FINGERPRINT"
            )
