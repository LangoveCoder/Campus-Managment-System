"""
Class Group Model
Constitution Section 2.5

A cohort of students in a specific cycle (e.g. "Grade 7 Blue").
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class ClassGroup(BaseCampusModel):
    """
    Represents a cohort of students.
    
    Constitution Rules:
    - Belongs to ONE AcademicCycle
    - Campus-scoped
    - Unique together: (academic_cycle, name, section)
    """
    academic_cycle = models.ForeignKey(
        'AcademicCycle',
        on_delete=models.CASCADE,
        related_name='class_groups'
    )
    
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=50, null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_class_groups'
        unique_together = ['academic_cycle', 'name', 'section']
        verbose_name = 'Class Group'
        verbose_name_plural = 'Class Groups'
        
    def __str__(self):
        if self.section:
            return f"{self.name} {self.section}"
        return self.name
