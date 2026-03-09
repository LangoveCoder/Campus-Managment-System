from celery import shared_task

@shared_task(name='admissions.notify_decision')
def notify_decision(application_id, decision, campus_id):
    """Notify applicant of admission decision."""
    from modules.admissions.services import AdmissionsQueryService
    app = AdmissionsQueryService.get_application(application_id, campus_id)
    if not app:
        return f"Application {application_id} not found"
    # TODO: wire to email/SMS when notification service is ready
    return f"Decision '{decision}' notification queued for {app.applicant_name}"

@shared_task(name='admissions.flag_stale_applications')
def flag_stale_applications():
    """Log stale applications with no action for 14+ days."""
    from django.utils import timezone
    from datetime import timedelta
    from modules.admissions.models import AdmissionApplication
    
    cutoff = timezone.now() - timedelta(days=14)
    stale = AdmissionApplication.objects.filter(
        status='PENDING',
        submitted_at__lt=cutoff
    )
    count = stale.count()
    return f"Found {count} stale applications older than 14 days"
