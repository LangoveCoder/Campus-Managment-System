from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from kernel.models import Person, UserAccount, Campus, Role, UserRoleBinding, BiometricIdentity
from kernel.services import IdentityService, BiometricService
import json
import uuid

class Phase6IntegrationTest(TestCase):
    def setUp(self):
        # Setup Campus
        self.campus = Campus.objects.create(name="Integration Campus", address="123 Test Lane")
        
        # Setup Roles
        self.role_student = Role.objects.get(name='student')
        self.role_teacher = Role.objects.get(name='teacher')
        
        # Setup Admin User for API calls
        self.admin_person = Person.objects.create(first_name="Admin", last_name="User", primary_email="admin@test.com")
        self.admin_user = UserAccount.objects.create_superuser(
            person=self.admin_person, username="admin_integ", email="admin@test.com", password="password123"
        )
        self.client = Client()
        self.client.login(username="admin_integ", password="password123")

    def test_full_student_journey(self):
        """
        Scenario: New Student Admission -> Enrollment -> Login -> Access
        """
        print("\n--- Starting Student Integration Journey ---")
        
        # 1. Create Person (Admission)
        person = IdentityService.create_person(
            first_name="John", last_name="Doe", 
            primary_email="john.doe@example.com", primary_phone="555-0100"
        )
        self.assertIsNotNone(person.id)
        print("1. Person Created ✅")

        # 2. Assign Role (binding)
        binding = UserRoleBinding.objects.create(
            person=person, role=self.role_student, campus=self.campus,
            created_by=self.admin_person
        )
        self.assertTrue(binding.is_active)
        print("2. Student Role Assigned ✅")

        # 3. Create Login
        user = UserAccount.objects.create_user(
            person=person, username="johndoe", password="studentpass123"
        )
        print("3. User Account Created ✅")

        # 4. Biometric Enrollment (via Service)
        # Verify Quality
        quality = BiometricService.verify_quality(b"mock_fingerprint_data")
        self.assertGreater(quality, 0.8)
        
        # Enroll
        bio = BiometricService.enroll_biometric(
            person_id=person.id, 
            biometric_type='fingerprint', 
            biometric_data=b"mock_fingerprint_data"
        )
        self.assertIsNotNone(bio)
        print("4. Biometrics Enrolled ✅")

        # 5. Biometric Authentication
        auth_person = BiometricService.authenticate_biometric(
            biometric_type='fingerprint', 
            biometric_data=b"mock_fingerprint_data"
        )
        self.assertEqual(auth_person.id, person.id)
        print("5. Biometric Auth Successful ✅")

        # 6. Context Access Check
        # Student login
        student_client = Client()
        student_client.login(username="johndoe", password="studentpass123")
        
        # Try to access dashboard with correct context
        session = student_client.session
        session['active_campus_id'] = self.campus.id
        session.save()
        
        # Mock a protected view access (simplified check)
        # In a real app we'd hit a generic view, here we simulate the permission check
        has_access = UserRoleBinding.get_active_bindings(person.id, self.campus.id).exists()
        self.assertTrue(has_access)
        print("6. Context Access Verified ✅")

    def test_campus_isolation(self):
        """
        Scenario: Data from Campus A should not be visible in Campus B
        """
        print("\n--- Starting Campus Isolation Test ---")
        campus_b = Campus.objects.create(name="Other Campus")
        
        # Teacher at Campus A
        teacher = IdentityService.create_person(first_name="Alice", last_name="Teach")
        UserRoleBinding.objects.create(person=teacher, role=self.role_teacher, campus=self.campus, created_by=self.admin_person)
        
        # Verify access to A
        bindings_a = UserRoleBinding.get_active_bindings(teacher.id, self.campus.id)
        self.assertTrue(bindings_a.exists())
        
        # Verify NO access to B
        bindings_b = UserRoleBinding.get_active_bindings(teacher.id, campus_b.id)
        self.assertFalse(bindings_b.exists())
        print("7. Campus Isolation Verified ✅")
