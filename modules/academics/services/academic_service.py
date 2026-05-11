from django.db import transaction
from kernel.facades import AuthorizationFacade
from ..models import AcademicProgram, AcademicCycle, ClassGroup

class AcademicService:
    @staticmethod
    def create_program(person_id: int, campus_id: int, name: str, code: str,
                       program_type: str, assessment_scheme_id: int,
                       description: str = "", duration_years: int = None) -> AcademicProgram:
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='academics.create_program'
        )
        return AcademicProgram.objects.create(
            campus_id=campus_id,
            name=name,
            code=code,
            program_type=program_type,
            assessment_scheme_id=assessment_scheme_id,
            description=description,
            duration_years=duration_years or None,
        )

    @staticmethod
    def create_cycle(person_id: int, campus_id: int, program_id: int, name: str, sequence: int, start_date, end_date) -> AcademicCycle:
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='academics.create_program'
        )
        return AcademicCycle.objects.create(
            campus_id=campus_id,
            academic_program_id=program_id,
            name=name,
            sequence=sequence,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def create_class_group(person_id: int, campus_id: int, cycle_id: int, name: str, capacity: int) -> ClassGroup:
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='academics.create_class_group'
        )
        return ClassGroup.objects.create(
            campus_id=campus_id,
            academic_cycle_id=cycle_id,
            name=name,
            capacity=capacity
        )
