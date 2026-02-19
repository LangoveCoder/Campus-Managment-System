"""
Student Profile Model
Constitution Section 2.6

Links a Person to an AcademicProgram.
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class StudentProfile(BaseCampusModel):
    """
    Represents a person as a learner in a program.
    
    Constitution Rules:
    - One Person may have multiple StudentProfiles (lifecycle)
    - Status-driven lifecycle
    - Campus-scoped
    - Admission number must be unique within campus
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('GRADUATED', 'Graduated'),
        ('WITHDRAWN', 'Withdrawn'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    person = models.ForeignKey(
        'kernel.Person',
        on_delete=models.PROTECT,
        related_name='student_profiles'
    )
    
    academic_program = models.ForeignKey(
        'AcademicProgram',
        on_delete=models.PROTECT,
        related_name='student_profiles'
    )
    
    admission_number = models.CharField(max_length=50)
    admission_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_student_profiles'
        unique_together = ['campus', 'admission_number']
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        
    def __str__(self):
        return f"{self.admission_number} - {self.person.full_name}"
