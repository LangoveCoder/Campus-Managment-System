
from django.db import models
from django.utils.translation import gettext_lazy as _
from kernel.models.base import BaseCampusModel
from .device import WorkforceAttendanceDevice

class WorkforceAttendanceEvent(BaseCampusModel):
    """
    Immutable log of raw check-in/check-out events.
    """
    class EventType(models.TextChoices):
        CHECK_IN = 'CHECK_IN', _('Check In')
        CHECK_OUT = 'CHECK_OUT', _('Check Out')

    class Source(models.TextChoices):
        FINGERPRINT = 'FINGERPRINT', _('Fingerprint')
        FACE = 'FACE', _('Face')
        MANUAL = 'MANUAL', _('Manual Override')

    person = models.ForeignKey('kernel.Person', on_delete=models.PROTECT, related_name='workforce_events')
    device = models.ForeignKey(WorkforceAttendanceDevice, on_delete=models.PROTECT, null=True, blank=True, related_name='events')
    
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    event_time = models.DateTimeField()
    source = models.CharField(max_length=20, choices=Source.choices)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['person', 'event_time']),
            models.Index(fields=['campus', 'event_time']),
        ]

    def __str__(self):
        return f"{self.person} - {self.event_type} @ {self.event_time}"

class WorkforceDailyAttendance(BaseCampusModel):
    """
    Aggregated daily summary for fast querying.
    """
    person = models.ForeignKey('kernel.Person', on_delete=models.PROTECT, related_name='workforce_daily_attendance')
    date = models.DateField()
    
    first_check_in = models.DateTimeField(null=True, blank=True)
    last_check_out = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['person', 'date'], name='unique_workforce_daily_attendance')
        ]

    def __str__(self):
        return f"{self.person} - {self.date}"
