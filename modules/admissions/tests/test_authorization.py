
from django.test import TestCase
from kernel.models import Person, Campus, Role, UserRoleBinding
from kernel.services import AuthorizationService
from modules.admissions.models import Applicant, AdmissionApplication
from modules.admissions.services import AdmissionsService
from kernel.exceptions import PermissionDenied
import datetime
from django.apps import apps

class AuthorizationTests(TestCase):
    def setUp(self):
        Permission = apps.get_model('kernel', 'Permission')
        # 1. Setup Campus and Person
        self.campus = Campus.objects.create(name="Auth Test Campus", campus_type="PHYSICAL")
        self.person = Person.objects.create(full_name="Staff User", primary_email="staff@example.com")
        self.unauthorized_person = Person.objects.create(full_name="Rando", primary_email="rando@example.com")
        
        # 2. Create Application to act upon
        self.applicant = Applicant.objects.create(full_name="Test Applicant", date_of_birth="2000-01-01", campus=self.campus)
        self.application = AdmissionApplication.objects.create(applicant=self.applicant, campus=self.campus, status="SUBMITTED")
        
        # 3. Define Permissions
        self.perm_evaluate = Permission.objects.create(module="admissions", code="evaluate_test", name="Evaluate")
        self.perm_decide = Permission.objects.create(module="admissions", code="make_decision", name="Decide")
        
        # 4. Assign Role to Person (Admissions Officer)
        self.role = Role.objects.create(name="Admissions Officer")
        self.role.permissions.add(self.perm_evaluate, self.perm_decide)
        
        # 5. Bind Person to Role at Campus
        UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            valid_from=datetime.date.today(),
            valid_until=None
        )

    def test_authorized_action(self):
        """
        Verify that a user with permission can perform the action.
        """
        # Should succeed
        result = AdmissionsService.evaluate_test_result(
            person_id=self.person.id,
            application_id=self.application.id,
            score=85.0
        )
        self.assertEqual(result.score, 85.0)
        
        # Should succeed
        decision = AdmissionsService.make_decision(
            person_id=self.person.id,
            application_id=self.application.id,
            decision="ACCEPTED"
        )
        self.assertEqual(decision.decision, "ACCEPTED")
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "ACCEPTED")
        print("\n✅ Authorization Test Passed: Authorized user successfully performed actions.")

    def test_unauthorized_action(self):
        """
        Verify that a user WITHOUT permission is blocked.
        """
        with self.assertRaises(PermissionDenied):
            AdmissionsService.evaluate_test_result(
                person_id=self.unauthorized_person.id,
                application_id=self.application.id,
                score=10.0
            )
        
        print("\n✅ Authorization Test Passed: Unauthorized user was blocked.")
