"""
Assessment Scheme Model
Constitution Section 3.1

A named evaluation strategy (e.g., "Three-Term Scheme").
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class AssessmentScheme(BaseCampusModel):
    """
    Container for evaluation strategy.
    
    Constitution Rules:
    - Campus-scoped
    - Configuration only (NO logic)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_assessment_schemes'
        verbose_name = 'Assessment Scheme'
        verbose_name_plural = 'Assessment Schemes'
        
    def __str__(self):
        return self.name
