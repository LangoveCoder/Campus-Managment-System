"""
Assessment Result Model
Constitution Section 3.4

Stores raw assessment scores only.
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class AssessmentResult(BaseCampusModel):
    """
    Raw marks for a student in an assessment.
    
    Constitution Rules:
    - Unique together: (enrollment, assessment_instance)
    - Stores ONLY raw marks
    - NO pass/fail, NO percentage, NO GPA
    """
    enrollment = models.ForeignKey(
        'Enrollment',
        on_delete=models.PROTECT,
        related_name='results'
    )
    
    assessment_instance = models.ForeignKey(
        'AssessmentInstance',
        on_delete=models.PROTECT,
        related_name='results'
    )
    
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    is_absent = models.BooleanField(default=False)
    remarks = models.TextField(null=True, blank=True)
    
    entered_by = models.ForeignKey(
        'kernel.Person',
        on_delete=models.PROTECT,
        related_name='entered_results'
    )
    
    entered_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_assessment_results'
        unique_together = ['enrollment', 'assessment_instance']
        verbose_name = 'Assessment Result'
        verbose_name_plural = 'Assessment Results'
        
    def __str__(self):
        return f"{self.marks_obtained} - {self.enrollment.student_profile.admission_number}"
