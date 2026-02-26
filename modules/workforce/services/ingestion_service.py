
import hashlib
from django.utils import timezone
from django.db import transaction
from modules.workforce.models import WorkforceAttendanceDevice, WorkforceAttendanceEvent, WorkforceDailyAttendance
from kernel.exceptions import AuthorizationException

class BiometricIngestionService:
    @staticmethod
    def authenticate_device(token: str) -> WorkforceAttendanceDevice:
        """
        Authenticates a device by its API token.
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        try:
            device = WorkforceAttendanceDevice.objects.get(api_token=token_hash, is_active=True)
            device.last_heartbeat = timezone.now()
            device.save(update_fields=['last_heartbeat'])
            return device
        except WorkforceAttendanceDevice.DoesNotExist:
            raise AuthorizationException("Invalid Device Token")

    @staticmethod
    @transaction.atomic
    def ingest_event(device_token: str, person_id: int, event_type: str, event_time, source: str):
        """
        Ingests a raw event from a device.
        Updates the Daily Summary.
        """
        device = BiometricIngestionService.authenticate_device(device_token)
        
        # Log Immutable Event
        event = WorkforceAttendanceEvent.objects.create(
            campus_id=device.campus_id,
            device=device,
            person_id=person_id,
            event_type=event_type,
            event_time=event_time,
            source=source
        )
        
        # Update Daily Summary (Idempotent-ish)
        # We need to find or create the daily record
        daily_record, created = WorkforceDailyAttendance.objects.get_or_create(
            campus_id=device.campus_id,
            person_id=person_id,
            date=event_time.date()
        )
        
        # Logic: First check-in is min(event_time), Last check-out is max(event_time)
        # Actually, simpler:
        # If CHECK_IN: if first_check_in is None or time < first_check_in -> update
        # If CHECK_OUT: if last_check_out is None or time > last_check_out -> update
        
        if event_type == 'CHECK_IN':
            if not daily_record.first_check_in or event_time < daily_record.first_check_in:
                daily_record.first_check_in = event_time
                daily_record.save()
                
        elif event_type == 'CHECK_OUT':
            if not daily_record.last_check_out or event_time > daily_record.last_check_out:
                daily_record.last_check_out = event_time
                daily_record.save()
                
        return event


class WorkforceIngestionService:
    """
    JWT-gated staff-facing punch service.
    Accepts device_id directly (no device_token lookup).
    Raw log storage only — no HR logic, no lateness calculation.
    """

    @staticmethod
    @transaction.atomic
    def staff_punch(
        person_id: int,
        campus_id: int,
        device_id: int,
        target_person_id: int,
        punch_type: str,
        event_time,
    ) -> WorkforceAttendanceEvent:
        """
        Records a raw punch event on behalf of a staff member.

        person_id        — API caller (must have manage_attendance)
        campus_id        — campus context from session
        device_id        — device being punched on
        target_person_id — the staff member being punched in/out
        punch_type       — CHECK_IN or CHECK_OUT
        event_time       — datetime of the punch
        Auth enforced internally.
        """
        from modules.workforce.auth import AuthorizationFacade
        AuthorizationFacade.require(person_id, campus_id, 'manage_attendance')

        device = WorkforceAttendanceDevice.objects.get(id=device_id, campus_id=campus_id)

        event = WorkforceAttendanceEvent.objects.create(
            campus_id=campus_id,
            device=device,
            person_id=target_person_id,
            event_type=punch_type,
            event_time=event_time,
            source='STAFF',
        )

        # Update daily summary — same logic as BiometricIngestionService.ingest_event
        daily_record, _ = WorkforceDailyAttendance.objects.get_or_create(
            campus_id=campus_id,
            person_id=target_person_id,
            date=event_time.date(),
        )

        if punch_type == 'CHECK_IN':
            if not daily_record.first_check_in or event_time < daily_record.first_check_in:
                daily_record.first_check_in = event_time
                daily_record.save()
        elif punch_type == 'CHECK_OUT':
            if not daily_record.last_check_out or event_time > daily_record.last_check_out:
                daily_record.last_check_out = event_time
                daily_record.save()

        return event

