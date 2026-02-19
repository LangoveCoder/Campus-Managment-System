"""
Assessment Instance Model
Constitution Section 3.3

A specific occurrence of an assessment period for a class.
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class AssessmentInstance(BaseCampusModel):
    """
    Scheduled assessment event.
    
    Constitution Rules:
    - Links AssessmentPeriod to ClassGroup
    - Campus-isolated
    - Unique together: (class_group, assessment_period, course_offering, scheduled_date)
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONDUCTED', 'Conducted'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    class_group = models.ForeignKey(
        'ClassGroup',
        on_delete=models.PROTECT,
        related_name='assessment_instances'
    )
    
    assessment_period = models.ForeignKey(
        'AssessmentPeriod',
        on_delete=models.PROTECT,
        related_name='instances'
    )
    
    course_offering = models.ForeignKey(
        'CourseOffering',
        on_delete=models.PROTECT,
        related_name='assessment_instances'
    )
    
    scheduled_date = models.DateField(null=True, blank=True)
    conducted_date = models.DateField(null=True, blank=True)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    is_retake = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_assessment_instances'
        unique_together = ['class_group', 'assessment_period', 'course_offering', 'scheduled_date']
        verbose_name = 'Assessment Instance'
        verbose_name_plural = 'Assessment Instances'
        
    def __str__(self):
        return f"{self.assessment_period.name} for {self.class_group} - {self.course_offering.course.code}"
