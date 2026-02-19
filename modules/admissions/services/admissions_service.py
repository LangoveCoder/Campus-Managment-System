
from typing import Dict, Optional, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from kernel.models import Person
from ..models import (
    Applicant, 
    AdmissionApplication, 
    AdmissionTestResult, 
    InterviewEvaluation, 
    AdmissionDecision
)
from ..auth import AuthorizationFacade

class AdmissionsService:
    """
    Service layer for Admissions Module.
    Encapsulates all business logic and enforces authorization via AuthorizationFacade.
    """

    @staticmethod
    def submit_application(
        full_name: str,
        dob: str,
        campus_id: int,
        form_payload: Dict[str, Any],
        contact_info: Dict[str, Any] = None,
        guardian_info: Dict[str, Any] = None,
        academic_program_id: Optional[int] = None
    ) -> AdmissionApplication:
        """
        Public-facing method to submit an application.
        Does NOT require intense authorization (usually public/anonymous), 
        but if an agent is doing it, they need 'admissions.submit_application' (if we tracked that).
        For this Constitutional Build, we assume this is a system action or public action.
        """
        # 1. Create Applicant (Minimal Identity)
        applicant = Applicant.objects.create(
            full_name=full_name,
            date_of_birth=dob,
            campus_id=campus_id,
            contact_info=contact_info or {},
            guardian_info=guardian_info or {}
        )

        # 2. Create Application
        application = AdmissionApplication.objects.create(
            applicant=applicant,
            campus_id=campus_id,
            academic_program_id=academic_program_id,
            form_payload=form_payload,
            status=AdmissionApplication.Status.SUBMITTED
        )

        return application

    @staticmethod
    def evaluate_test_result(
        person_id: int,
        application_id: int,
        score: float,
        total_score: float = 100.0,
        rank: Optional[int] = None,
        source: str = 'Internal'
    ) -> AdmissionTestResult:
        """
        Record a test result.
        Requires: admissions.evaluate_test
        """
        application = AdmissionApplication.objects.get(id=application_id)
        
        # Authorization Check
        AuthorizationFacade.require(person_id, application.campus_id, 'evaluate_test')

        result = AdmissionTestResult.objects.create(
            campus_id=application.campus_id,
            application=application,
            score=score,
            total_score=total_score,
            rank=rank,
            source=source
        )

        # Auto-update status if needed (Business Rule: Tested)
        if application.status == AdmissionApplication.Status.SUBMITTED:
            application.status = AdmissionApplication.Status.TESTED
            application.save()
            
        return result

    @staticmethod
    def conduct_interview(
        person_id: int,
        application_id: int,
        remarks: str,
        recommendation: str
    ) -> InterviewEvaluation:
        """
        Log an interview.
        Requires: admissions.conduct_interview
        """
        application = AdmissionApplication.objects.get(id=application_id)
        
        # Authorization Check
        AuthorizationFacade.require(person_id, application.campus_id, 'conduct_interview')

        interviewer = Person.objects.get(id=person_id)

        evaluation = InterviewEvaluation.objects.create(
            campus_id=application.campus_id,
            application=application,
            interviewer=interviewer,
            remarks=remarks,
            recommendation=recommendation
        )

        # Update status
        application.status = AdmissionApplication.Status.INTERVIEWED
        application.save()

        return evaluation

    @staticmethod
    def make_decision(
        person_id: int,
        application_id: int,
        decision: str, # ACCEPTED, REJECTED, WAITLISTED
        comments: str = ""
    ) -> AdmissionDecision:
        """
        Final Verdict.
        Requires: admissions.make_decision
        """
        application = AdmissionApplication.objects.get(id=application_id)
        
        # Authorization Check
        AuthorizationFacade.require(person_id, application.campus_id, 'make_decision')

        decider = Person.objects.get(id=person_id)

        # Create Decision Record
        verdict = AdmissionDecision.objects.create(
            campus_id=application.campus_id,
            application=application,
            decision=decision,
            decided_by=decider,
            comments=comments
        )

        # Update Application Status
        application.status = decision
        application.save()

        # If ACCEPTED, we could trigger enrollment conversion here OR make it a separate step.
        # Constitution says: "Only after acceptance does the student become part of Academics."
        # Implementation Plan says: "convert_to_student" is a separate manual or auto step.

        return verdict

    @staticmethod
    def convert_to_enrollment(
        person_id: int,
        application_id: int
    ):
        """
        Handoff to Academics Module.
        Requires: admissions.convert_to_enrollment
        Only allowed if Status == ACCEPTED.
        """
        application = AdmissionApplication.objects.get(id=application_id)
        
        # Authorization Check
        AuthorizationFacade.require(person_id, application.campus_id, 'convert_to_enrollment')

        if application.status != AdmissionApplication.Status.ACCEPTED:
            raise ValidationError("Application must be ACCEPTED before enrollment.")

        # Service Call to Academics (Mock / Stub for now as per instructions "stub")
        # In a real scenario, this would import AcademicsEnrollmentService
        # from modules.academics.services import EnrollmentService
        
        # For now, we just return a success message or mock object
        return {
            "status": "success", 
            "message": f"Application {application_id} queued for enrollment in Academics."
        }
