"""
Test Authorization
Constitution Section 8.1
"""
from django.test import TestCase
from django.core.exceptions import PermissionDenied
from kernel.models import Person, Campus
from modules.academics.services import EnrollmentService
# We don't import AuthorizationService here directly anymore as the Service uses the Facade internally
# But we can verify that the Service still works as expected (calls Facade -> calls Kernel)

class AuthorizationTest(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(name="C1")
        self.person = Person.objects.create(full_name="Attacker", primary_email="bad@a.com")
        self.teacher = Person.objects.create(full_name="Teacher", primary_email="t@a.com")

    def test_enrollment_denied(self):
        """Test that enrollment fails without permission."""
        # We don't verify setup logic here, just that Service calls Auth Requirement
        # Since we haven't assigned any roles to 'person', they have NO permissions.
        
        # Attempt to call create_enrollment
        with self.assertRaises(PermissionDenied):
            EnrollmentService.create_enrollment(
                student_profile_id=1, # Dummy ID
                class_group_id=1, 
                campus_id=self.campus.id, 
                person_id=self.person.id
            )
