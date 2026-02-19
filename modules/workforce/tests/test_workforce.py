
from django.test import TestCase
from django.utils import timezone
from django.apps import apps
from kernel.exceptions import AuthorizationException, PermissionDeniedException as PermissionDenied
from modules.workforce.services.device_service import DeviceRegistrationService
from modules.workforce.services.ingestion_service import BiometricIngestionService

class WorkforceTests(TestCase):
    def setUp(self):
        Person = apps.get_model('kernel', 'Person')
        Campus = apps.get_model('kernel', 'Campus')
        Role = apps.get_model('kernel', 'Role')
        Permission = apps.get_model('kernel', 'Permission')
        
        self.campus = Campus.objects.create(name="Workforce Campus")
        self.admin = Person.objects.create(first_name="Admin", last_name="User", campus=self.campus)
        self.staff = Person.objects.create(first_name="Staff", last_name="Member", campus=self.campus)
        self.hacker = Person.objects.create(first_name="Hacker", last_name="Man", campus=self.campus)
        
        # Grant permissions
        p1 = Permission.objects.get(module='workforce', code='workforce.manage_devices')
        p2 = Permission.objects.get(module='workforce', code='workforce.view_attendance')
        
        role = Role.objects.create(name="Workforce Admin", campus=self.campus)
        role.permissions.add(p1, p2)
        
        from kernel.services.role_binding_service import RoleBindingService
        RoleBindingService.assign_role(self.admin.id, self.campus.id, role.id)

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
        summary = apps.get_model('modules.workforce', 'WorkforceDailyAttendance').objects.get(
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
        
        summary.refresh_from_db()
        self.assertEqual(summary.last_check_out, later)

    def test_unauthorized_access(self):
        """Test authorization barriers."""
        with self.assertRaises(PermissionDenied):
            DeviceRegistrationService.register_device(
                person_id=self.hacker.id,
                campus_id=self.campus.id,
                name="Hacker Device",
                device_type="FINGERPRINT"
            )
