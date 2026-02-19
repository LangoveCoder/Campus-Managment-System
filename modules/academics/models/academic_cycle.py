"""
Academic Cycle Model
Constitution Section 2.2

A repeatable time unit inside a program (e.g., "Year 1", "Semester 2").
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class AcademicCycle(BaseCampusModel):
    """
    Represents a repeatable time unit inside a program.
    
    Constitution Rules:
    - Belongs to ONE AcademicProgram
    - Ordered by sequence
    - Time bounds are informational
    - Unique together: (academic_program, sequence)
    """
    academic_program = models.ForeignKey(
        'AcademicProgram',
        on_delete=models.CASCADE,
        related_name='cycles'
    )
    
    name = models.CharField(max_length=100)
    sequence = models.IntegerField(help_text="ordering sequence (1, 2, 3...)")
    
    # Informational dates for reporting
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_cycles'
        unique_together = [
            ('academic_program', 'sequence'),
            ('academic_program', 'name')
        ]
        ordering = ['sequence']
        verbose_name = 'Academic Cycle'
        verbose_name_plural = 'Academic Cycles'
        
    def __str__(self):
        return f"{self.academic_program.code} - {self.name}"
