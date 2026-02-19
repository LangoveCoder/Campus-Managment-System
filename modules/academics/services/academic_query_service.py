"""
Academic Query Service
Constitution Section 7.1

Read-only helper methods for academic data.
"""
from typing import List, Optional
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
