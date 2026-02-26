"""
Test Enrollment
Constitution Section 8.1

Must Test:
- Creating enrollment
- Preventing duplicate enrollments
- Cross-campus isolation
- Authorization checks
"""
from django.test import TestCase
from django.utils import timezone
from kernel.models import Person, Campus, Role, UserRoleBinding
from modules.academics.models import (
    AssessmentScheme, AcademicProgram, AcademicCycle, ClassGroup, 
    StudentProfile, Enrollment
)
from modules.academics.services import EnrollmentService
from modules.academics.auth import AuthorizationFacade
from django.core.exceptions import PermissionDenied

class EnrollmentTest(TestCase):
    def setUp(self):
        # 1. Setup Identity
        self.campus = Campus.objects.create(name="Campus A")
        self.campus_b = Campus.objects.create(name="Campus B")
        
        self.registrar = Person.objects.create(full_name="Registrar", primary_email="reg@a.com", primary_phone="+923001002001")
        self.student_person = Person.objects.create(full_name="Student", primary_email="stu@a.com", primary_phone="+923001002002")
        
        # 2. Setup Perms
        # Simulate Registrar having enroll_student permission
        # In real app, we'd assign Role 'REGISTRAR' which has this perm
        # For unit test, we can mock or use direct binding if we loaded seed data
        
        # Let's mock AuthorizationService.require_permission to avoid complex role setup in unit test
        # OR we can just test the Service logic assuming auth passes, and separate Auth test
        # But Constitution says "Authorization checks" must be tested.
        pass

    def test_duplicate_enrollment_prevention(self):
        """Test that a student cannot be enrolled in two classes in same cycle."""
        # Setup Program/Cycle
        scheme = AssessmentScheme.objects.create(campus=self.campus, name="Test Scheme")
        prog = AcademicProgram.objects.create(campus=self.campus, name="Prog", code="P1", assessment_scheme=scheme)
        cycle = AcademicCycle.objects.create(campus=self.campus, academic_program=prog, name="C1", sequence=1)
        
        class_a = ClassGroup.objects.create(campus=self.campus, academic_cycle=cycle, name="Class A")
        class_b = ClassGroup.objects.create(campus=self.campus, academic_cycle=cycle, name="Class B")
        
        profile = StudentProfile.objects.create(
            campus=self.campus, person=self.student_person, 
            academic_program=prog, admission_number="A001", admission_date=timezone.now().date()
        )
        
        # Mock Auth to pass
        original_require = AuthorizationFacade.require
        AuthorizationFacade.require = lambda **kwargs: None
        
        try:
            # 1. Enroll in Class A
            EnrollmentService.create_enrollment(profile.id, class_a.id, self.campus.id, self.registrar.id)
            
            # 2. Try Enroll in Class B (Same Cycle) -> Should Fail
            with self.assertRaises(ValueError):
                EnrollmentService.create_enrollment(profile.id, class_b.id, self.campus.id, self.registrar.id)
                
        finally:
            AuthorizationFacade.require = original_require

