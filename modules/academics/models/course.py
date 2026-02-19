"""
Course Model
Constitution Section 2.3

A reusable subject/content taught across programs (e.g., "Mathematics").
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class Course(BaseCampusModel):
    """
    Represents abstract subject content.
    
    Constitution Rules:
    - Campus-scoped
    - Reusable across multiple programs
    - NO grading logic
    - NO credit hours
    - Code must be unique within campus
    """
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_courses'
        unique_together = ['campus', 'code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        
    def __str__(self):
        return f"{self.code} - {self.name}"
