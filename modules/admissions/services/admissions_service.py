from modules.admissions.utils import format_cnic

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
from kernel.facades import AuthorizationFacade

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
        academic_program_id: Optional[int] = None,
        # New flat fields
        father_name: str = '',
        cnic: str = '',
        district: str = '',
        marks=None,
        date_of_birth=None,
        contact_number: str = '',
        address: str = '',
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
            status=AdmissionApplication.Status.SUBMITTED,
            father_name=father_name,
            cnic=cnic,
            district=district,
            marks=marks or None,
            date_of_birth=date_of_birth or None,
            contact_number=contact_number,
            address=address,
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
        AuthorizationFacade.require(person_id, application.campus_id, 'admissions.evaluate_test')

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
        AuthorizationFacade.require(person_id, application.campus_id, 'admissions.conduct_interview')

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
        AuthorizationFacade.require(person_id, application.campus_id, 'admissions.make_decision')

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
        application_id: int,
        program_id: int = None,
        class_group_id: int = None
    ):
        """
        Handoff to Academics Module.
        Requires: admissions.convert_to_enrollment
        Only allowed if Status == ACCEPTED.
        """
        application = AdmissionApplication.objects.get(id=application_id)
        
        # Authorization Check
        AuthorizationFacade.require(person_id, application.campus_id, 'admissions.convert_to_enrollment')

        if application.status != AdmissionApplication.Status.ACCEPTED:
            raise ValidationError("Application must be ACCEPTED before enrollment.")

        if not program_id and not application.academic_program_id:
            raise ValidationError("A target academic program is required for enrollment.")
            
        target_program_id = program_id or application.academic_program_id

        with transaction.atomic():
            # 1. Create Person
            import uuid
            phone = application.contact_number
            if not phone:
                phone = f"TMP-{uuid.uuid4().hex[:8]}"
                
            from kernel.models import Person
            person = Person.objects.create(
                full_name=application.applicant.full_name,
                primary_phone=phone,
                date_of_birth=application.date_of_birth or application.applicant.date_of_birth or '2000-01-01',
            )
            
            # 2. Assign Campus Identity
            from modules.campus_identity.services import CampusIdentityService
            campus_person = CampusIdentityService.add_person_to_campus(str(person.id), str(application.campus_id))
            
            # 3. Create StudentProfile
            from modules.academics.models import StudentProfile
            from django.utils import timezone
            
            student_profile = StudentProfile.objects.create(
                campus_id=application.campus_id,
                person=person,
                academic_program_id=target_program_id,
                admission_number=campus_person.campus_identifier,
                admission_date=timezone.now().date(),
                status='ACTIVE'
            )
            
            # Enroll in the user-selected ClassGroup, or fall back to first active
            from modules.academics.models import ClassGroup, Enrollment
            if class_group_id:
                active_class = ClassGroup.objects.filter(
                    campus_id=application.campus_id,
                    id=class_group_id,
                    is_active=True
                ).first()
            else:
                active_class = ClassGroup.objects.filter(
                    campus_id=application.campus_id,
                    academic_cycle__academic_program_id=target_program_id,
                    is_active=True
                ).first()
            
            if active_class:
                Enrollment.objects.create(
                    campus_id=application.campus_id,
                    student_profile=student_profile,
                    class_group=active_class,
                    enrollment_date=timezone.now().date(),
                    status='ACTIVE'
                )
            
            # 4. Update Application Status
            application.academic_program_id = target_program_id
            application.status = AdmissionApplication.Status.ENROLLED
            application.save()
            
            return {
                "status": "success", 
                "message": f"Application {application_id} converted. Student ID: {campus_person.campus_identifier}."
            }


    @staticmethod
    def calculate_merit_score(application_id, campus_id):
        from modules.admissions.models import AdmissionApplication, AdmissionConfig
        app = AdmissionApplication.objects.get(id=application_id, campus_id=campus_id)
        
        # Get config — program-specific first, then campus default
        config = AdmissionConfig.objects.filter(
            campus_id=campus_id,
            academic_program=app.academic_program
        ).first() or AdmissionConfig.objects.filter(
            campus_id=campus_id,
            academic_program=None
        ).first()
        
        if not config or not app.marks:
            return None
        
        if config.interview_type == 'QUALIFYING':
            score = app.marks
        else:
            interview = app.interview_marks or 0
            score = (app.marks * config.test_weight) + (interview * config.interview_weight)
        
        app.merit_score = score
        app.save(update_fields=['merit_score'])
        return score

    @staticmethod
    def process_merit_list(person_id: int, campus_id: int, csv_file) -> dict:
        """
        Reads a CSV file and creates new MERIT_LISTED applications.
        Expects a CSV with headers: name, father_name, cnic, district, marks.
        """
        AuthorizationFacade.require(person_id, campus_id, 'admissions.make_decision')
        
        decoded_file = csv_file.read().decode('utf-8-sig')
        import csv
        import io
        reader = csv.DictReader(io.StringIO(decoded_file))
        
        headers = [h.lower().strip() for h in (reader.fieldnames or [])]
        required = ['name', 'father_name', 'cnic', 'district', 'marks']
        missing = [req for req in required if req not in headers]
        if missing:
            raise ValidationError(f"CSV is missing required columns: {', '.join(missing)}")
            
        imported = 0
        skipped = 0
        
        with transaction.atomic():
            for row in reader:
                row_clean = {k.lower().strip(): v.strip() for k, v in row.items() if k}
                cnic = format_cnic(row_clean.get('cnic', ''))
                
                if not cnic:
                    skipped += 1
                    continue
                    
                if AdmissionApplication.objects.filter(cnic=cnic, campus_id=campus_id).exists():
                    skipped += 1
                    continue
                
                applicant = Applicant.objects.create(
                    full_name=row_clean.get('name', 'Unknown'),
                    date_of_birth='2000-01-01',  # Default placeholder
                    campus_id=campus_id
                )
                
                marks_val = row_clean.get('marks')
                if not marks_val:
                    marks_val = None
                    
                from django.utils import timezone
                
                AdmissionApplication.objects.create(
                    applicant=applicant,
                    campus_id=campus_id,
                    father_name=row_clean.get('father_name', ''),
                    cnic=cnic,
                    district=row_clean.get('district', ''),
                    marks=marks_val,
                    status=AdmissionApplication.Status.MERIT_LISTED,
                    form_payload={'full_name': row_clean.get('name', 'Unknown')},
                )
                imported += 1
                    
        return {
            'imported': imported,
            'skipped': skipped
        }

    @staticmethod
    def get_applications(campus_id: int, person_id: int):
        """
        Returns all AdmissionApplications scoped to campus_id, newest first.
        Auth is the caller's responsibility — view checks permission before calling.
        """
        return AdmissionApplication.objects.filter(
            campus_id=campus_id,
        ).select_related('applicant').order_by('-submitted_at')

    @staticmethod
    def get_application_by_id(
        application_id: int,
        campus_id: int,
        person_id: int,
    ) -> AdmissionApplication:
        """
        Returns a single AdmissionApplication scoped to campus.
        Raises ValidationError if not found or campus mismatch.
        Auth is the caller's responsibility — view checks permission before calling.
        """
        try:
            return AdmissionApplication.objects.select_related('applicant').get(
                id=application_id,
                campus_id=campus_id,
            )
        except AdmissionApplication.DoesNotExist:
            raise ValidationError(
                f'Application {application_id} not found at this campus.'
            )

