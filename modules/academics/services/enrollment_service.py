"""
Enrollment Service
Constitution Section 7.1

Manages student enrollment in classes.
"""
from typing import List, Optional
from django.db import transaction
from django.utils import timezone
from django.db import transaction
from django.utils import timezone
from kernel.facades import AuthorizationFacade
from ..models import Enrollment, StudentProfile, ClassGroup

class EnrollmentService:
    @staticmethod
    def create_enrollment(
        student_profile_id: int, 
        class_group_id: int, 
        campus_id: int, 
        person_id: int
    ) -> Enrollment:
        """
        Enroll a student in a class.
        
        Enforces:
        - Authorization
        - Unique enrollment per cycle
        """
        # 1. Authorization
        # 1. Authorization
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='academics.enroll_student'
        )
        
        # 2. Get entities to validte context
        student = StudentProfile.objects.get(id=student_profile_id, campus_id=campus_id)
        class_group = ClassGroup.objects.get(id=class_group_id, campus_id=campus_id)
        
        # 3. Rule: One class per cycle per student
        # Check if already enrolled in ANY class in this cycle
        existing = Enrollment.objects.filter(
            student_profile=student,
            class_group__academic_cycle=class_group.academic_cycle,
            status='ACTIVE'
        ).exclude(class_group=class_group)
        
        if existing.exists():
            raise ValueError(f"Student already enrolled in {existing.first().class_group} for this cycle")
            
        # 4. Create
        enrollment, created = Enrollment.objects.get_or_create(
            student_profile=student,
            class_group=class_group,
            defaults={
                'enrollment_date': timezone.now().date(),
                'status': 'ACTIVE',
                'campus_id': campus_id
            }
        )
        
        if not created and enrollment.status != 'ACTIVE':
            enrollment.status = 'ACTIVE'
            enrollment.save()
            
        return enrollment

    @staticmethod
    def withdraw_enrollment(
        enrollment_id: int, 
        reason: str, 
        campus_id: int, 
        person_id: int
    ) -> None:
        """
        Withdraw a student from a class.
        """
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='academics.delete_enrollment' # Using dangerous perm for withdrawal
        )
        
        enrollment = Enrollment.objects.get(id=enrollment_id, campus_id=campus_id)
        enrollment.status = 'WITHDRAWN'
        enrollment.save()

    @staticmethod
    def get_enrollment_by_id(
        enrollment_id: int,
        campus_id: int,
        person_id: int,
    ) -> 'Enrollment':
        """
        Return a single Enrollment scoped to campus.
        Raises django.core.exceptions.ValidationError if not found or wrong campus.
        Auth is the caller's responsibility — view checks permission before calling.
        """
        from django.core.exceptions import ValidationError
        try:
            return Enrollment.objects.get(id=enrollment_id, campus_id=campus_id)
        except Enrollment.DoesNotExist:
            raise ValidationError(
                f'Enrollment {enrollment_id} not found at this campus.'
            )

