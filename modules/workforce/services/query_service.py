
from modules.workforce.models import WorkforceAttendanceEvent, WorkforceDailyAttendance
from kernel.facades import AuthorizationFacade

class WorkforceAttendanceQueryService:
    @staticmethod
    def get_daily_attendance(person_id: int, campus_id: int, date):
        """
        Get daily attendance for a specific person.
        """
        AuthorizationFacade.require(person_id, campus_id, 'workforce.view_attendance')
        try:
            return WorkforceDailyAttendance.objects.get(campus_id=campus_id, person_id=person_id, date=date)
        except WorkforceDailyAttendance.DoesNotExist:
            return None

    @staticmethod
    def get_event_log(person_id: int, campus_id: int, target_person_id: int):
        """
        Get raw event logs for a person.
        """
        AuthorizationFacade.require(person_id, campus_id, 'workforce.view_attendance')
        return WorkforceAttendanceEvent.objects.filter(campus_id=campus_id, person_id=target_person_id).order_by('-event_time')

    @staticmethod
    def get_event_log_by_range(
        person_id: int,
        campus_id: int,
        date_from,
        date_to,
        target_person_id: int = None,
    ):
        """
        Returns WorkforceAttendanceEvents for a campus filtered by date range.
        Optionally filter to a specific target_person_id.
        Auth enforced internally.
        """
        AuthorizationFacade.require(person_id, campus_id, 'workforce.view_attendance')

        filters = dict(
            campus_id=campus_id,
            event_time__date__range=(date_from, date_to),
        )
        if target_person_id is not None:
            filters['person_id'] = target_person_id

        return WorkforceAttendanceEvent.objects.filter(**filters).order_by('-event_time')

    @staticmethod
    def get_summary_by_range(
        person_id: int,
        campus_id: int,
        date_from,
        date_to,
        target_person_id: int = None,
    ) -> dict:
        """
        Returns aggregated punch counts grouped by person across a date range.
        Result structure: { "results": [ { "person_id": X, "total_in": N, "total_out": N } ] }
        Auth enforced internally.
        """
        from django.db.models import Count, Q

        AuthorizationFacade.require(person_id, campus_id, 'workforce.view_attendance')

        filters = dict(
            campus_id=campus_id,
            event_time__date__range=(date_from, date_to),
        )
        if target_person_id is not None:
            filters['person_id'] = target_person_id

        results = (
            WorkforceAttendanceEvent.objects
            .filter(**filters)
            .values('person_id')
            .annotate(
                total_in=Count('id', filter=Q(event_type='CHECK_IN')),
                total_out=Count('id', filter=Q(event_type='CHECK_OUT')),
            )
            .order_by('person_id')
        )

        return {
            'date_from': str(date_from),
            'date_to': str(date_to),
            'results': [
                {
                    'person_id': str(r['person_id']),
                    'total_in': r['total_in'],
                    'total_out': r['total_out'],
                }
                for r in results
            ],
        }

