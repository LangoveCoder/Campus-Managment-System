
from django.test import TestCase
from django.apps import apps
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from kernel.exceptions import PermissionDenied, BusinessRuleViolation
from modules.attendance.models import AttendanceSession, AttendanceRecord

class AttendanceLedgerTests(TestCase):
    def setUp(self):
        # 1. Setup Kernel Data
        Person = apps.get_model('kernel', 'Person')
        UserAccount = apps.get_model('kernel', 'UserAccount')
        Campus = apps.get_model('kernel', 'Campus')
        Role = apps.get_model('kernel', 'Role')
        Permission = apps.get_model('kernel', 'Permission')
        
        self.campus = Campus.objects.create(name="Attendance Campus")
        self.teacher = Person.objects.create(first_name="Teacher", last_name="One", campus=self.campus)
        self.student_person = Person.objects.create(first_name="Student", last_name="One", campus=self.campus)
        self.hacker = Person.objects.create(first_name="Hacker", last_name="Access", campus=self.campus)
        
        # 2. Setup Academics Data (Mocking the structure)
        AcademicProgram = apps.get_model('academics', 'AcademicProgram')
        AcademicCycle = apps.get_model('academics', 'AcademicCycle')
        ClassGroup = apps.get_model('academics', 'ClassGroup')
        StudentProfile = apps.get_model('academics', 'StudentProfile')
        Enrollment = apps.get_model('academics', 'Enrollment')
        
        self.program = AcademicProgram.objects.create(name="Matric", campus=self.campus, program_type="MATRIC")
        self.cycle = AcademicCycle.objects.create(name="2026", campus=self.campus, start_date="2026-01-01", end_date="2026-12-31")
        self.class_group = ClassGroup.objects.create(name="10-A", campus=self.campus, program=self.program, cycle=self.cycle)
        
        self.student_profile = StudentProfile.objects.create(person=self.student_person, campus=self.campus, enrollment_number="ST-001")
        Enrollment.objects.create(student=self.student_profile, class_group=self.class_group, status='ACTIVE', enrollment_date="2026-01-01")
        
        # 3. Setup Permissions
        # We need to assign 'attendance.create_session' and 'attendance.mark_attendance' to teacher
        # Mocking the AuthorizationService lookup essentially implies we need to seed the DB permissions first
        # But we are using AuthorizationFacade which checks Kernel. AuthorizationService.
        # We'll grant permissions directly via UserRoleBinding (if we were full integration testing)
        # OR we can mock AuthorizationFacade for unit testing scope.
        # Strict instructions say "DO NOT import kernel authorization services directly", but
        # for Integration Tests, we should rely on the real system.
        
        # Grant teacher the permissions
        # Create permissions
        p1 = Permission.objects.get(module='attendance', code='create_session')
        p2 = Permission.objects.get(module='attendance', code='mark_attendance')
        
        # Create Role and Binding
        teacher_role = Role.objects.create(name="Teacher", campus=self.campus)
        teacher_role.permissions.add(p1, p2)
        
        from kernel.services.role_binding_service import RoleBindingService
        RoleBindingService.assign_role(self.teacher.id, self.campus.id, teacher_role.id)

    def test_session_creation(self):
        """Test strict session creation."""
        from modules.attendance.services import AttendanceSessionService
        
        session = AttendanceSessionService.create_session(
            person_id=self.teacher.id,
            campus_id=self.campus.id,
            class_group_id=self.class_group.id,
            attendance_date="2026-02-20"
        )
        self.assertIsNotNone(session.id)
        self.assertEqual(session.taken_by, self.teacher)
        
    def test_unauthorized_action(self):
        """Test strict authorization enforcement."""
        from modules.attendance.services import AttendanceSessionService
        from kernel.exceptions import PermissionDenied
        
        with self.assertRaises(PermissionDenied):
            AttendanceSessionService.create_session(
                person_id=self.hacker.id,
                campus_id=self.campus.id,
                class_group_id=self.class_group.id,
                attendance_date="2026-02-20"
            )

    def test_ledger_integrity(self):
        """Test Constraint: UNIQUE(session, student)."""
        from modules.attendance.services import AttendanceSessionService, AttendanceMarkingService
        
        session = AttendanceSessionService.create_session(
            person_id=self.teacher.id,
            campus_id=self.campus.id,
            class_group_id=self.class_group.id,
            attendance_date="2026-02-20"
        )
        
        # Mark once
        AttendanceMarkingService.mark_bulk(
            person_id=self.teacher.id,
            campus_id=self.campus.id,
            session_id=session.id,
            attendance_data=[{'student_id': self.student_profile.id, 'status': 'PRESENT'}]
        )
        
        # Mark again - Should FAIL (Ledger Immutable Rule for duplicates)
        with self.assertRaises(BusinessRuleViolation):
            AttendanceMarkingService.mark_bulk(
                person_id=self.teacher.id,
                campus_id=self.campus.id,
                session_id=session.id,
                attendance_data=[{'student_id': self.student_profile.id, 'status': 'PRESENT'}]
            )

    def test_student_validation(self):
        """Test validation: Student must be in ClassGroup."""
        from modules.attendance.services import AttendanceSessionService, AttendanceMarkingService
        
        # Create unassigned student
        other_person = apps.get_model('kernel', 'Person').objects.create(first_name="Other", last_name="Student", campus=self.campus)
        other_profile = apps.get_model('academics', 'StudentProfile').objects.create(person=other_person, campus=self.campus, enrollment_number="ST-002")
        # No enrollment in 10-A
        
        session = AttendanceSessionService.create_session(
            person_id=self.teacher.id,
            campus_id=self.campus.id,
            class_group_id=self.class_group.id,
            attendance_date="2026-02-20"
        )
        
        with self.assertRaises(ValidationError):
            AttendanceMarkingService.mark_bulk(
                person_id=self.teacher.id,
                campus_id=self.campus.id,
                session_id=session.id,
                attendance_data=[{'student_id': other_profile.id, 'status': 'PRESENT'}]
            )
