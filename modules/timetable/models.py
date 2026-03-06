import uuid
from django.db import models

DAY_CHOICES = [
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
]

PERIOD_CHOICES = [(str(i), f'Period {i}') for i in range(1, 9)]
class Room(models.Model):
    campus_id = models.IntegerField()
    name = models.CharField(max_length=100)  # e.g. "Room 4", "Physics Lab"
    capacity = models.PositiveIntegerField(default=30)
    room_type = models.CharField(max_length=20, choices=[
        ('CLASSROOM', 'Classroom'),
        ('LAB', 'Laboratory'),
        ('HALL', 'Hall'),
    ], default='CLASSROOM')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [('campus_id', 'name')]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.room_type})"


class TimetableSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campus_id = models.IntegerField()
    class_group_id = models.IntegerField()
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    period = models.CharField(max_length=1, choices=PERIOD_CHOICES)
    course_name = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100, blank=True)
    teacher = models.ForeignKey('kernel.Person', null=True, blank=True, on_delete=models.SET_NULL)
    room = models.CharField(max_length=50, blank=True)
    room_fk = models.ForeignKey(Room, null=True, blank=True, on_delete=models.SET_NULL)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = [('campus_id', 'class_group_id', 'day', 'period')]
        ordering = ['day', 'period']

    def __str__(self):
        return f"{self.day} P{self.period} — {self.course_name}"
