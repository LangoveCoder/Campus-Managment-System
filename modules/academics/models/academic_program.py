"""
Academic Program Model
Constitution Section 2.1

A complete academic track from start to finish.
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class AcademicProgram(BaseCampusModel):
    """
    Represents a complete academic track (e.g., "BS Computer Science").
    
    Constitution Rules:
    - Campus-scoped (via BaseCampusModel)
    - Linked to ONE AssessmentScheme
    - Code must be unique within campus
    """
    PROGRAM_TYPES = [
        ('PRIMARY', 'Primary Education'),
        ('SECONDARY', 'Secondary Education'),
        ('COLLEGE', 'College / Intermediate'),
        ('UNIVERSITY', 'University / Higher Ed'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    
    # Informational only, not enforced
    duration_years = models.IntegerField(null=True, blank=True)
    
    # Linked Scheme (Constitution 3.1)
    # Using string reference to avoid circular imports if model not yet loaded
    assessment_scheme = models.ForeignKey(
        'academics.AssessmentScheme',
        on_delete=models.PROTECT,
        related_name='programs'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_programs'
        unique_together = ['campus', 'code']
        verbose_name = 'Academic Program'
        verbose_name_plural = 'Academic Programs'
        
    def __str__(self):
        return f"{self.code} - {self.name}"
