
from django.db import models
from django.utils.translation import gettext_lazy as _
from kernel.models.base import BaseCampusModel

class AttendanceSession(BaseCampusModel):
    """
    Represents one attendance-taking event.
    Reflects: "Class 10-A, English, 2026-02-20"
    """
    class SessionType(models.TextChoices):
        DAILY = 'DAILY', _('Daily')
        PERIOD = 'PERIOD', _('Period')
        SUBJECT = 'SUBJECT', _('Subject')

    class Source(models.TextChoices):
        MANUAL = 'MANUAL', _('Manual')
        BIOMETRIC = 'BIOMETRIC', _('Biometric')
        FACIAL = 'FACIAL', _('Facial')

    # Foreign Keys
    class_group = models.ForeignKey('academics.ClassGroup', on_delete=models.PROTECT, related_name='attendance_sessions')
    course_offering = models.ForeignKey('academics.CourseOffering', on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_sessions')
    taken_by = models.ForeignKey('kernel.Person', on_delete=models.PROTECT, related_name='taken_attendance_sessions')

    # Data Fields
    attendance_date = models.DateField()
    session_type = models.CharField(max_length=20, choices=SessionType.choices, default=SessionType.DAILY)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.attendance_date} - {self.class_group} ({self.session_type})"

class AttendanceRecord(BaseCampusModel):
    """
    One row per student per session.
    The strict Ledger of Facts.
    """
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', _('Present')
        ABSENT = 'ABSENT', _('Absent')
        LATE = 'LATE', _('Late')
        EXCUSED = 'EXCUSED', _('Excused')

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey('academics.StudentProfile', on_delete=models.PROTECT, related_name='attendance_records')
    
    status = models.CharField(max_length=20, choices=Status.choices)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'student'], name='unique_session_student_attendance')
        ]

    def __str__(self):
        return f"{self.student} - {self.status}"
