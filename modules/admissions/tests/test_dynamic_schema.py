
from django.test import TestCase
from kernel.models import Person, Campus
from modules.admissions.models import Applicant, AdmissionApplication
from modules.admissions.services import AdmissionsService

class DynamicSchemaTests(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(name="Test Campus", campus_type="PHYSICAL")
        self.person = Person.objects.create(full_name="Test User", primary_email="test@example.com")

    def test_dynamic_payloads(self):
        """
        Verify that two applications can have completely different schemas.
        Constitution: "Applications are NOT fixed."
        """
        # Payload 1: Matric System (Science)
        payload_1 = {
             "board": "BSEK",
             "group": "Science",
             "subjects": ["Physics", "Chemistry", "Math", "Biology"],
             "metrics": {
                 "ninth_grade_marks": 450,
                 "total": 550
             }
        }
        
        # Payload 2: O-Level System (Arts)
        payload_2 = {
             "exam_board": "Cambridge",
             "subjects": [
                 {"name": "History", "grade": "A"},
                 {"name": "Geography", "grade": "B"},
                 {"name": "English", "grade": "A*"}
             ],
             "extra_curricular": ["Debate Club"]
        }
        
        # Submit App 1
        app_1 = AdmissionsService.submit_application(
            full_name="Student One",
            dob="2010-01-01",
            campus_id=self.campus.id,
            form_payload=payload_1
        )
        
        # Submit App 2
        app_2 = AdmissionsService.submit_application(
            full_name="Student Two",
            dob="2010-05-05",
            campus_id=self.campus.id,
            form_payload=payload_2
        )
        
        # Refresh and Verify
        app_1.refresh_from_db()
        app_2.refresh_from_db()
        
        # Assertions
        # 1. Verify Payload 1 integrity
        self.assertEqual(app_1.form_payload['board'], "BSEK")
        self.assertEqual(app_1.form_payload['metrics']['ninth_grade_marks'], 450)
        
        # 2. Verify Payload 2 integrity
        self.assertEqual(app_2.form_payload['exam_board'], "Cambridge")
        self.assertEqual(app_2.form_payload['subjects'][0]['grade'], "A")
        
        # 3. Verify no cross-pollution (App 1 shouldn't have exam_board)
        self.assertNotIn('exam_board', app_1.form_payload)
        
        print("\n✅ Dynamic Schema Test Passed: Two apps with totally different structures stored successfully.")

    def test_applicant_minimalism(self):
        """
        Verify Applicant model does not contain academic fields.
        Constitution: "Applicant Represents human BEFORE student. NO academic fields."
        """
        applicant = Applicant.objects.create(
            full_name="Minimal Guy",
            date_of_birth="2000-01-01",
            campus=self.campus
        )
        
        # Check attributes via introspection
        # This is a meta-test to ensure no one added 'marks' or 'grade' fields to the model.
        fields = [f.name for f in Applicant._meta.get_fields()]
        
        forbidden_terms = ['marks', 'grade', 'class', 'section', 'roll_number', 'program']
        for term in forbidden_terms:
            self.assertNotIn(term, fields, f"❌ VIOLATION: Applicant model contains forbidden academic field '{term}'")
            
        print("\n✅ Applicant Minimalism Test Passed: No academic fields found in Applicant model.")
