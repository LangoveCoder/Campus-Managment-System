
from modules.workforce.models import WorkforceAttendanceEvent, WorkforceDailyAttendance
from modules.workforce.auth import AuthorizationFacade

class WorkforceAttendanceQueryService:
    @staticmethod
    def get_daily_attendance(person_id: int, campus_id: int, date):
        """
        Get daily attendance for a specific person.
        """
        AuthorizationFacade.require(person_id, campus_id, 'view_attendance')
        try:
            return WorkforceDailyAttendance.objects.get(campus_id=campus_id, person_id=person_id, date=date)
        except WorkforceDailyAttendance.DoesNotExist:
            return None

    @staticmethod
    def get_event_log(person_id: int, campus_id: int, target_person_id: int):
        """
        Get raw event logs for a person.
        """
        AuthorizationFacade.require(person_id, campus_id, 'view_attendance')
        return WorkforceAttendanceEvent.objects.filter(campus_id=campus_id, person_id=target_person_id).order_by('-event_time')
