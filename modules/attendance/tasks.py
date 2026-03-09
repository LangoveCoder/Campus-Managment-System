from celery import shared_task

@shared_task(name='attendance.daily_summary')
def generate_daily_summary():
    """Generate daily attendance summary for all campuses."""
    from kernel.models import Campus
    from modules.attendance.services import AttendanceQueryService
    results = []
    for campus in Campus.objects.filter(is_active=True):
        summary = AttendanceQueryService.get_summary(str(campus.id))
        results.append(f"Campus {campus.name}: {summary}")
    return results

@shared_task(name='attendance.generate_report')
def generate_attendance_report(campus_id, class_group_id):
    """Generate attendance report async for large class groups."""
    from modules.attendance.services import AttendanceQueryService
    report = AttendanceQueryService.get_summary(campus_id)
    return report
