"""
Course Offering Model
Constitution Section 2.4

Links a Course to an AcademicProgram (Curriculum Intent).
"""
from django.db import models
from kernel.models.base import BaseCampusModel

class CourseOffering(BaseCampusModel):
    """
    Represents curriculum intent - which courses are part of which programs.
    
    Constitution Rules:
    - Links Course to Program (not Cycle)
    - Unique together: (course, academic_program)
    - Required vs elective is data, not enforcement
    """
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='offerings'
    )
    
    academic_program = models.ForeignKey(
        'AcademicProgram',
        on_delete=models.CASCADE,
        related_name='course_offerings'
    )
    
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_course_offerings'
        unique_together = ['course', 'academic_program']
        verbose_name = 'Course Offering'
        verbose_name_plural = 'Course Offerings'
        
    def __str__(self):
        return f"{self.course.code} in {self.academic_program.code}"
