"""
Assessment Service
Constitution Section 7.1

Manages assessment instances and results.
"""
from typing import List, Optional
from decimal import Decimal
from datetime import date
from django.utils import timezone
from ..auth import AuthorizationFacade
from ..models import (
    AssessmentInstance, AssessmentResult, Enrollment, 
    ClassGroup, AssessmentPeriod, CourseOffering
)
from kernel.models import Person

class AssessmentService:
    @staticmethod
    def create_assessment_instance(
        class_group_id: int,
        assessment_period_id: int,
        course_offering_id: int,
        max_marks: Decimal,
        scheduled_date: date,
        campus_id: int,
        person_id: int
    ) -> AssessmentInstance:
        """
        Schedule an assessment.
        """
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='academics.create_program' # Approximate perm, maybe should add specific one
        )
        
        # Validate existence and scope
        class_group = ClassGroup.objects.get(id=class_group_id, campus_id=campus_id)
        period = AssessmentPeriod.objects.get(id=assessment_period_id) 
        # Note: Period is child of Scheme, Scheme is Campus Scoped.
        if period.assessment_scheme.campus_id != campus_id:
             raise ValueError("Assessment Period from different campus")
             
        offering = CourseOffering.objects.get(id=course_offering_id, campus_id=campus_id)
        
        instance, created = AssessmentInstance.objects.get_or_create(
            class_group=class_group,
            assessment_period=period,
            course_offering=offering,
            scheduled_date=scheduled_date,
            defaults={
                'max_marks': max_marks,
                'campus_id': campus_id,
                'status': 'SCHEDULED'
            }
        )
        return instance

    @staticmethod
    def enter_result(
        enrollment_id: int,
        assessment_instance_id: int,
        marks_obtained: Decimal,
        entered_by_person_id: int,
        campus_id: int
    ) -> AssessmentResult:
        """
        Enter a raw score.
        """
        AuthorizationFacade.require(
            person_id=entered_by_person_id,
            campus_id=campus_id,
            permission_code='academics.enter_assessment_result'
        )
        
        instance = AssessmentInstance.objects.get(id=assessment_instance_id, campus_id=campus_id)
        enrollment = Enrollment.objects.get(id=enrollment_id, campus_id=campus_id)
        entered_by = Person.objects.get(id=entered_by_person_id) # Kernel model
        
        # Validation
        if marks_obtained > instance.max_marks:
            raise ValueError(f"Marks {marks_obtained} exceed max {instance.max_marks}")
            
        result, created = AssessmentResult.objects.update_or_create(
            enrollment=enrollment,
            assessment_instance=instance,
            defaults={
                'marks_obtained': marks_obtained,
                'entered_by': entered_by,
                'campus': instance.campus, # Ensure result is in same campus
                'entered_at': timezone.now()
            }
        )
        return result

    @staticmethod
    def get_results_summary_by_class(
        person_id: int,
        campus_id: int,
        class_group_id: int,
        assessment_instance_id: int,
    ) -> dict:
        """
        GAP 4 — Aggregated results summary for one assessment instance,
        scoped to a class group and campus.

        Authorization is enforced internally — callers must supply a valid person_id.
        Absent students (is_absent=True) are excluded from avg/highest/lowest
        to avoid distorting statistics.
        """
        from django.db.models import Avg, Max, Min
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='academics.view_student_results',
        )

        results = AssessmentResult.objects.filter(
            campus_id=campus_id,
            assessment_instance_id=assessment_instance_id,
            enrollment__class_group_id=class_group_id,
        )

        total_results = results.count()
        present_results = results.filter(is_absent=False)

        aggregates = present_results.aggregate(
            average=Avg('marks_obtained'),
            highest=Max('marks_obtained'),
            lowest=Min('marks_obtained'),
        )

        return {
            'total_results': total_results,
            'average': float(aggregates['average']) if aggregates['average'] is not None else None,
            'highest': float(aggregates['highest']) if aggregates['highest'] is not None else None,
            'lowest': float(aggregates['lowest']) if aggregates['lowest'] is not None else None,
            'absent_count': total_results - present_results.count(),
        }
