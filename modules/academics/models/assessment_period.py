"""
Assessment Period Model
Constitution Section 3.2

Defines the assessment moments within a scheme (e.g., "Mid-Term").
"""
from django.db import models

class AssessmentPeriod(models.Model):
    """
    Checkpoints within a scheme.
    
    Constitution Rules:
    - Belongs to ONE AssessmentScheme
    - Ordered by sequence
    - Weight is DATA, not logic
    - Unique together: (assessment_scheme, sequence)
    """
    # Does NOT inherit BaseCampusModel directly because it is a child of AssessmentScheme
    # However, since AssessmentScheme is campus-scoped, this is implicitly scoped.
    # Constitution definition does *not* list campus FK for this model explicitly, 
    # unlike others where it says "inherited from BaseCampusModel".
    # Checking definition: "id, assessment_scheme, name..." - NO campus field listed.
    
    assessment_scheme = models.ForeignKey(
        'AssessmentScheme',
        on_delete=models.CASCADE,
        related_name='periods'
    )
    
    name = models.CharField(max_length=100)
    sequence = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_assessment_periods'
        unique_together = ['assessment_scheme', 'sequence']
        ordering = ['sequence']
        verbose_name = 'Assessment Period'
        verbose_name_plural = 'Assessment Periods'
        
    def __str__(self):
        return f"{self.assessment_scheme.name} - {self.name}"
