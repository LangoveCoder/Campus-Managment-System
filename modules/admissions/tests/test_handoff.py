
from django.test import TestCase
from unittest.mock import patch
from kernel.models import Person, Campus, Role, UserRoleBinding, RolePermissionMap
from modules.admissions.models import Applicant, AdmissionApplication
from modules.admissions.services import AdmissionsService
from modules.academics.models import AcademicProgram, AssessmentScheme
from django.core.exceptions import ValidationError
import datetime
from django.apps import apps

class HandoffTests(TestCase):
    def setUp(self):
        Permission = apps.get_model('kernel', 'Permission')
        self.campus = Campus.objects.create(name="Handoff Campus", campus_type="PHYSICAL")
        self.person = Person.objects.create(full_name="Registrar", primary_email="registrar@example.com")
        
        self.perm_enroll, _ = Permission.objects.get_or_create(
            module="admissions", code="admissions.convert_to_enrollment",
            defaults={"name": "Enroll"},
        )
        self.role = Role.objects.create(name="Registrar")
        RolePermissionMap.objects.create(role=self.role, permission=self.perm_enroll)
        
        UserRoleBinding.objects.create(
            person=self.person, role=self.role, campus=self.campus
        )
        
        self.applicant = Applicant.objects.create(full_name="Future Student", date_of_birth="2005-01-01", campus=self.campus)
        self.scheme = AssessmentScheme.objects.create(name="Test Scheme", campus=self.campus)
        self.program = AcademicProgram.objects.create(name="Test Program", program_type="BACHELORS", duration_years=4, assessment_scheme=self.scheme, campus=self.campus)

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
        
        # Mock external dependencies
        with patch('kernel.models.Person.objects.create') as mock_person, \
             patch('modules.campus_identity.services.CampusIdentityService.add_person_to_campus') as mock_identity, \
             patch('modules.academics.models.StudentProfile.objects.create') as mock_profile:
             
            # Setup mocks
            from unittest.mock import MagicMock
            mock_identity.return_value = MagicMock(campus_identifier='TEST-123')
            
            result = AdmissionsService.convert_to_enrollment(self.person.id, app_2.id, program_id=self.program.id)
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('TEST-123', result['message'])
        
        print("\n✅ Handoff Test Passed: Only ACCEPTED applications can be enrolled.")
