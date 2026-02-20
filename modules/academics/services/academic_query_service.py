"""
Academic Query Service
Constitution Section 7.1

Read-only helper methods for academic data.
"""
from typing import List, Optional
from django.db.models import Q
from django.utils import timezone
from kernel.exceptions import AuthorizationException
from django.db.models import QuerySet
from ..auth import AuthorizationFacade
from ..models import (
    StudentProfile, ClassGroup, Course, Enrollment, 
    TeachingAssignment, AcademicProgram, AcademicCycle
)
from kernel.models import Person

class AcademicQueryService:
    @staticmethod
    def get_students_in_class(person_id: int, class_group_id: int, campus_id: int) -> QuerySet[StudentProfile]:
        """
        Get all active students enrolled in a class.
        Caller must provide an authenticated person_id.
        """
        if person_id is None:
            raise AuthorizationException("Authentication required: person_id must not be None.")

        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='academics.view_program'
        )

        return StudentProfile.objects.filter(
            campus_id=campus_id,
            enrollments__class_group_id=class_group_id,
            enrollments__status='ACTIVE'
        )

    @staticmethod
    def get_classes_for_student(student_profile_id: int, campus_id: int) -> QuerySet[ClassGroup]:
        """
        Get all active classes for a student.
        """
        return ClassGroup.objects.filter(
            campus_id=campus_id,
            enrollments__student_profile_id=student_profile_id,
            enrollments__status='ACTIVE'
        )

    @staticmethod
    def get_teachers_for_class(class_group_id: int, campus_id: int) -> QuerySet[Person]:
        """
        Get all teachers assigned to a class.
        """
        return Person.objects.filter(
            teaching_assignments__class_group_id=class_group_id,
            teaching_assignments__campus_id=campus_id,
            teaching_assignments__is_active=True
        ).distinct()

    @staticmethod
    def get_courses_for_class(class_group_id: int, campus_id: int) -> QuerySet[Course]:
        """
        Get all courses taught in a class.
        """
        return Course.objects.filter(
            offerings__teaching_assignments__class_group_id=class_group_id,
            offerings__teaching_assignments__campus_id=campus_id,
            offerings__teaching_assignments__is_active=True
        ).distinct()

    # -----------------------------------------------------------------------
    # Campus-level count methods (dashboard use — caller must check auth)
    # -----------------------------------------------------------------------

    @staticmethod
    def get_enrolled_student_count(campus_id: int) -> int:
        """
        GAP 1 — Total active enrollments scoped to campus.
        Auth is the caller's responsibility (DashboardHomeView checks before calling).
        """
        return Enrollment.objects.filter(
            campus_id=campus_id,
            status='ACTIVE',
        ).count()

    @staticmethod
    def get_active_class_group_count(campus_id: int) -> int:
        """
        GAP 2 — Count of ClassGroups at campus whose AcademicCycle is currently active.
        'Active' = cycle.is_active is True AND (end_date is null OR end_date >= today).
        Auth is the caller's responsibility (DashboardHomeView checks before calling).
        """
        today = timezone.now().date()
        return ClassGroup.objects.filter(
            campus_id=campus_id,
            is_active=True,
            academic_cycle__is_active=True,
        ).filter(
            Q(academic_cycle__end_date__isnull=True) |
            Q(academic_cycle__end_date__gte=today)
        ).count()
