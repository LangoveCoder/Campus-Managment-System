import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from kernel.models import Person, Campus, Role, UserRoleBinding
from modules.academics.models import (
    AcademicProgram, AcademicCycle, ClassGroup, 
    StudentProfile, Enrollment, AssessmentScheme
)

class Command(BaseCommand):
    help = 'Seeds development data for academic records'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Extending seed data...")

        # 1. Get existing campus
        campus = Campus.objects.first()
        if not campus:
            self.stdout.write(self.style.ERROR("No campus found. Run other seeds first."))
            return

        # 2. Get existing AssessmentScheme (Requirement for AcademicProgram)
        # We saw ID 1 is 'Three-Term Scheme' in previous shell run
        scheme = AssessmentScheme.objects.filter(name='Three-Term Scheme').first()
        if not scheme:
            scheme = AssessmentScheme.objects.first()
        
        if not scheme:
            self.stdout.write(self.style.ERROR("No AssessmentScheme found. Ensure academics fixtures are loaded."))
            return

        # 3. Create AcademicProgram
        program, created = AcademicProgram.objects.get_or_create(
            campus=campus,
            code="FSC-PE",
            defaults={
                "name": "FSc Pre-Engineering",
                "program_type": "COLLEGE",
                "assessment_scheme": scheme,
                "is_active": True
            }
        )
        if created:
            self.stdout.write(f"Created AcademicProgram: {program.name}")

        # 4. Create AcademicCycle
        cycle, created = AcademicCycle.objects.get_or_create(
            academic_program=program,
            sequence=1,
            defaults={
                "campus": campus,
                "name": "2025-26",
                "start_date": date(2025, 8, 1),
                "end_date": date(2026, 6, 30),
                "is_active": True
            }
        )
        if created:
            self.stdout.write(f"Created AcademicCycle: {cycle.name}")

        # 5. Create 3 ClassGroups
        class_names = ["Grade 11 - A", "Grade 11 - B", "Grade 12 - A"]
        classes = []
        for name in class_names:
            cg, created = ClassGroup.objects.get_or_create(
                academic_cycle=cycle,
                name=name,
                defaults={
                    "campus": campus,
                    "capacity": 30,
                    "is_active": True
                }
            )
            classes.append(cg)
            if created:
                self.stdout.write(f"Created ClassGroup: {cg.name}")

        # 6. Create 10 Students (Person + StudentProfile + Enrollment)
        students_created = 0
        enrollments_created = 0

        for i in range(1, 11):
            email = f"student{i}@dev.local"
            name = f"Student {self.number_to_word(i)}"
            
            person, p_created = Person.objects.get_or_create(
                primary_email=email,
                defaults={
                    "full_name": name,
                    "primary_phone": f"+9230000000{i:02d}",
                    "date_of_birth": date(2008, 1, 1) + timedelta(days=i*30),
                    "is_active": True
                }
            )
            
            profile, sp_created = StudentProfile.objects.get_or_create(
                campus=campus,
                admission_number=f"2025-{i:04d}",
                defaults={
                    "person": person,
                    "academic_program": program,
                    "admission_date": date(2025, 8, 1),
                    "status": "ACTIVE"
                }
            )
            if sp_created:
                students_created += 1

            # Distribution: Cycle through classes for even distribution
            target_class = classes[(i-1) % len(classes)]
            
            enrollment, e_created = Enrollment.objects.get_or_create(
                student_profile=profile,
                class_group=target_class,
                defaults={
                    "campus": campus,
                    "enrollment_date": date.today(),
                    "status": "ACTIVE"
                }
            )
            if e_created:
                enrollments_created += 1

        # 7. Add Academics Permissions to Admin Role
        from kernel.models import Permission, RolePermissionMap
        
        admin_role = Role.objects.filter(name='SUPER_ADMIN').first()
        if admin_role:
            perms_to_add = [
                ('academics.view_class', 'Can view class details'),
                ('academics.enroll_student', 'Can enroll students'),
                ('academics.view_enrollment', 'Can view enrollments'),
                ('academics.manage_assessment', 'Can manage assessments'),
                ('academics.enter_assessment_result', 'Can enter assessment results'),
                ('academics.view_student_results', 'Can view student results'),
            ]
            for code, name in perms_to_add:
                perm, _ = Permission.objects.get_or_create(
                    module='academics',
                    code=code,
                    defaults={'name': name}
                )
                RolePermissionMap.objects.get_or_create(
                    role=admin_role,
                    permission=perm,
                    defaults={'granted_by': None}
                )
            self.stdout.write(f"Added {len(perms_to_add)} academics permissions to SUPER_ADMIN role.")

        # 8. Add Attendance Permissions to Admin Role
            att_perms = [
                ('attendance.view_attendance', 'Can view attendance'),
                ('attendance.mark_attendance', 'Can mark attendance'),
                ('attendance.create_session', 'Can create attendance session'),
            ]
            for code, name in att_perms:
                perm, _ = Permission.objects.get_or_create(
                    module='attendance',
                    code=code,
                    defaults={'name': name}
                )
                RolePermissionMap.objects.get_or_create(
                    role=admin_role,
                    permission=perm,
                    defaults={'granted_by': None}
                )
            self.stdout.write(f"Added {len(att_perms)} attendance permissions to SUPER_ADMIN role.")

        # 9. Seed Assessment Data
        from modules.academics.models import AssessmentPeriod, AssessmentInstance, AssessmentResult, Course, CourseOffering
        
        course, _ = Course.objects.get_or_create(
            campus=campus,
            code="PHY-101",
            defaults={"name": "Physics", "description": "Introductory Physics", "is_active": True}
        )
        offering, _ = CourseOffering.objects.get_or_create(
            course=course,
            academic_program=program,
            defaults={"campus": campus}
        )
        
        period = AssessmentPeriod.objects.filter(name='Mid-Term').first()
        if not period:
            period = AssessmentPeriod.objects.filter(name__icontains='Mid').first()
            if not period:
                period = AssessmentPeriod.objects.first()
            
        grade_11_a = classes[0]
        
        instance, _ = AssessmentInstance.objects.get_or_create(
            assessment_period=period,
            class_group=grade_11_a,
            course_offering=offering,
            scheduled_date='2026-01-15',
            defaults={'campus': campus, 'max_marks': 100, 'status': 'CONDUCTED'}
        )

        admin_person = Person.objects.filter(primary_email='admin@dev.local').first()
        if not admin_person:
             admin_person = Person.objects.first()

        marks = [85, 72, 90, 68, 95, 88, 76, 82, 91, 79, 85, 93, 71]
        enrollments = Enrollment.objects.filter(class_group=grade_11_a, campus=campus)
        results_created = 0
        for enrollment, mark in zip(enrollments, marks):
            _, created = AssessmentResult.objects.get_or_create(
                assessment_instance=instance,
                enrollment=enrollment,
                defaults={
                    'campus': campus,
                    'marks_obtained': mark, 
                    'is_absent': False, 
                    'entered_by': admin_person
                }
            )
            if created:
                results_created += 1
                
        self.stdout.write(f"Added {results_created} assessment results.")

        self.stdout.write(self.style.SUCCESS("\nSEED DATA EXTENDED"))
        self.stdout.write(f"AcademicProgram: 1")
        self.stdout.write(f"AcademicCycle: 1")
        self.stdout.write(f"ClassGroups: {len(classes)}")
        self.stdout.write(f"Students created: {students_created}")
        self.stdout.write(f"Enrollments created: {enrollments_created}")
        self.stdout.write(f"AssessmentResults created: {results_created}")

    def number_to_word(self, n):
        words = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
        return words[n] if 0 <= n <= 10 else str(n)
