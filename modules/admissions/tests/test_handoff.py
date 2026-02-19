
from django.test import TestCase
from unittest.mock import patch
from kernel.models import Person, Campus, Role, UserRoleBinding
from modules.admissions.models import Applicant, AdmissionApplication
from modules.admissions.services import AdmissionsService
from django.core.exceptions import ValidationError
import datetime
from django.apps import apps

class HandoffTests(TestCase):
    def setUp(self):
        Permission = apps.get_model('kernel', 'Permission')
        self.campus = Campus.objects.create(name="Handoff Campus", campus_type="PHYSICAL")
        self.person = Person.objects.create(full_name="Registrar", primary_email="registrar@example.com")
        
        self.perm_enroll = Permission.objects.create(module="admissions", code="convert_to_enrollment", name="Enroll")
        self.role = Role.objects.create(name="Registrar")
        self.role.permissions.add(self.perm_enroll)
        
        UserRoleBinding.objects.create(
            person=self.person, role=self.role, campus=self.campus, 
            valid_from=datetime.date.today()
        )
        
        self.applicant = Applicant.objects.create(full_name="Future Student", date_of_birth="2005-01-01", campus=self.campus)

    def test_handoff_success(self):
        """
        Verify that ONLY Accepted applications can be converted.
        """
        # Case 1: Application is SUBMITTED (Not Accepted)
        app_1 = AdmissionApplication.objects.create(applicant=self.applicant, campus=self.campus, status="SUBMITTED")
        
        with self.assertRaises(ValidationError):
            AdmissionsService.convert_to_enrollment(self.person.id, app_1.id)
            
        # Case 2: Application is ACCEPTED
        app_2 = AdmissionApplication.objects.create(applicant=self.applicant, campus=self.campus, status="ACCEPTED")
        
        # We mock the actual Academics call since we are testing the Admissions logic boundary
        # In a real integration test, we would check if Enrollment record exists.
        result = AdmissionsService.convert_to_enrollment(self.person.id, app_2.id)
        
        self.assertEqual(result['status'], 'success')
        print("\n✅ Handoff Test Passed: Only ACCEPTED applications can be enrolled.")
