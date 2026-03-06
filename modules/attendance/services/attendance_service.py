
from django.db import transaction, IntegrityError
from kernel.exceptions import BusinessRuleViolation
from modules.attendance.models import AttendanceSession, AttendanceRecord
from kernel.facades import AuthorizationFacade

class AttendanceSessionService:
    @staticmethod
    def create_session(person_id: int, campus_id: int, class_group_id: int, attendance_date, session_type='DAILY', source='MANUAL'):
        """
        Creates a new attendance session.
        """
        AuthorizationFacade.require(person_id, campus_id, 'attendance.create_session')
        
        # Determine taken_by person (the user creating the session)
        # Note: In a real app, we might want to validate if this person is a teacher for this class,
        # but strictly speaking, any authorized user can take attendance.
        
        session = AttendanceSession.objects.create(
            campus_id=campus_id,
            class_group_id=class_group_id,
            taken_by_id=person_id,
            attendance_date=attendance_date,
            session_type=session_type,
            source=source
        )
        return session

class AttendanceMarkingService:
    @staticmethod
    @transaction.atomic
    def mark_bulk(person_id: int, campus_id: int, session_id: int, attendance_data: list[dict]):
        """
        Marks attendance for multiple students in a session.
        attendance_data = [{'student_id': 1, 'status': 'PRESENT'}, ...]

        IMPORTANT: Enrollment validation (confirming each student belongs to
        the session's ClassGroup) is the CALLER's responsibility. This service
        trusts the pre-validated list and enforces only campus isolation and
        the ledger's uniqueness constraint.
        """
        AuthorizationFacade.require(person_id, campus_id, 'attendance.mark_attendance')

        session = AttendanceSession.objects.select_related('class_group').get(id=session_id)

        # Validate session belongs to caller's campus
        if session.campus_id != campus_id:
             raise BusinessRuleViolation("Cannot mark attendance for a session in another campus.")

        records = [
            AttendanceRecord(
                campus_id=campus_id,
                session=session,
                student_id=entry['student_id'],
                status=entry['status']
            )
            for entry in attendance_data
        ]

        try:
            AttendanceRecord.objects.bulk_create(records)
        except IntegrityError:
            raise BusinessRuleViolation("Attendance already marked for some students in this session.")

        return len(records)

class AttendanceQueryService:
    @staticmethod
    def get_session_report(person_id: int, campus_id: int, session_id: int):
        AuthorizationFacade.require(person_id, campus_id, 'attendance.view_attendance')
        session = AttendanceSession.objects.prefetch_related('records').get(id=session_id)
        if session.campus_id != campus_id:
             raise BusinessRuleViolation("Access denied to session.")
        return session

    @staticmethod
    def get_summary_by_class_and_date_range(
        person_id: int,
        campus_id: int,
        class_group_id: int,
        date_from,
        date_to,
    ) -> dict:
        """
        GAP 3 — Attendance summary aggregated by class group and date range.
        Returns present, absent, and total session counts.

        Authorization is enforced internally — callers must supply a valid person_id.
        """
        AuthorizationFacade.require(person_id, campus_id, 'attendance.view_attendance')

        sessions = AttendanceSession.objects.filter(
            campus_id=campus_id,
            class_group_id=class_group_id,
            attendance_date__range=(date_from, date_to),
        )
        session_ids = sessions.values_list('id', flat=True)

        records = AttendanceRecord.objects.filter(session_id__in=session_ids)

        return {
            'total_sessions': sessions.count(),
            'present': records.filter(status='PRESENT').count(),
            'absent': records.filter(status='ABSENT').count(),
            'late': records.filter(status='LATE').count(),
            'excused': records.filter(status='EXCUSED').count(),
        }

    @staticmethod
    def get_sessions_for_class(person_id: int, campus_id: int, class_group_id: int):
        from django.db.models import Count, Q
        AuthorizationFacade.require(person_id, campus_id, 'attendance.view_attendance')
        return AttendanceSession.objects.filter(
            campus_id=campus_id,
            class_group_id=class_group_id
        ).select_related('taken_by', 'class_group').annotate(
            total_present=Count('records', filter=Q(records__status='PRESENT')),
            total_absent=Count('records', filter=Q(records__status='ABSENT'))
        ).order_by('-attendance_date', '-created_at')

    @staticmethod
    def get_student_attendance_history(person_id: int, campus_id: int, enrollment_id: int) -> dict:
        AuthorizationFacade.require(person_id, campus_id, 'attendance.view_attendance')

        records = AttendanceRecord.objects.filter(
            campus_id=campus_id,
            student__enrollments__id=enrollment_id,
        ).select_related('session').order_by('-session__attendance_date')

        total = records.count()
        present = records.filter(status='PRESENT').count()
        absent = records.filter(status='ABSENT').count()
        late = records.filter(status='LATE').count()
        
        percentage = 0
        if total > 0:
            percentage = round(((present + late) / total) * 100, 1)

        summary = {
            'present': present,
            'absent': absent,
            'late': late,
            'total': total,
            'percentage': percentage
        }

        return {
            'records': records,
            'summary': summary
        }

    @staticmethod
    def get_recent_sessions(person_id: int, campus_id: int, limit: int = 5):
        AuthorizationFacade.require(person_id, campus_id, 'attendance.view_attendance')
        return AttendanceSession.objects.filter(
            campus_id=campus_id
        ).select_related('class_group').order_by('-attendance_date')[:limit]
