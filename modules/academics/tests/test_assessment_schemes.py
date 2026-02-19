"""
Test Assessment Schemes
Constitution Section 8.1
"""
from django.test import TestCase
from modules.academics.models import AssessmentScheme, AssessmentPeriod, AcademicProgram
from kernel.models import Campus

class AssessmentSchemeTest(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(name="Campus A")

    def test_scheme_creation(self):
        """Test creating a scheme with periods."""
        scheme = AssessmentScheme.objects.create(campus=self.campus, name="3-Term")
        
        p1 = AssessmentPeriod.objects.create(assessment_scheme=scheme, name="Mid", sequence=1, weight=30.00)
        p2 = AssessmentPeriod.objects.create(assessment_scheme=scheme, name="Final", sequence=2, weight=70.00)
        
        self.assertEqual(scheme.periods.count(), 2)
        self.assertEqual(p1.weight, 30.00)
        
    def test_program_linking(self):
        """Test linking program to scheme."""
        scheme = AssessmentScheme.objects.create(campus=self.campus, name="Sem")
        prog = AcademicProgram.objects.create(
            campus=self.campus, name="CS", code="CS1", 
            program_type="UNIVERSITY", assessment_scheme=scheme
        )
        self.assertEqual(prog.assessment_scheme, scheme)
