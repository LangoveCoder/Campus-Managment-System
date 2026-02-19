"""
Enrollment Model
Constitution Section 2.7

Links StudentProfile to ClassGroup.
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class Enrollment(BaseCampusModel):
    """
    Represents student participation in a class.
    
    Constitution Rules:
    - Unique together: (student_profile, class_group)
    - A student can only be enrolled in one class per cycle (Logic enforced in Service)
    - Campus-isolated
    - Status tracks participation state
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('WITHDRAWN', 'Withdrawn'),
        ('TRANSFERRED', 'Transferred'),
    ]
    
    student_profile = models.ForeignKey(
        'StudentProfile',
        on_delete=models.PROTECT,
        related_name='enrollments'
    )
    
    class_group = models.ForeignKey(
        'ClassGroup',
        on_delete=models.PROTECT,
        related_name='enrollments'
    )
    
    enrollment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_enrollments'
        unique_together = ['student_profile', 'class_group']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        
    def __str__(self):
        return f"{self.student_profile} in {self.class_group}"
