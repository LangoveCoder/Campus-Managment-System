"""
Base Models for Campus-Scoped Entities

Provides abstract base models that include campus isolation functionality.
"""
from django.db import models
from .campus import Campus
from ..managers import CampusAwareManager


class BaseCampusModel(models.Model):
    """
    Abstract base model for campus-scoped entities.
    
    All models that should be isolated by campus should inherit from this.
    Provides:
    - Automatic campus field
    - Automatic campus filtering via CampusAwareManager
    - Index on campus field for performance
    
    Usage:
        class Student(BaseCampusModel):
            person = models.ForeignKey(Person, on_delete=models.PROTECT)
            student_id = models.CharField(max_length=20)
            # campus field is inherited automatically!
        
        # Queries are automatically filtered by current campus
        students = Student.objects.all()  # Only current campus
        all_students = Student.objects.all_campuses()  # All campuses
    """
    
    campus = models.ForeignKey(
        Campus,
        on_delete=models.PROTECT,
        related_name='%(class)s_set',
        help_text='Campus this record belongs to',
        db_index=True
    )
    
    # Use campus-aware manager by default
    objects = CampusAwareManager()
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['campus']),
        ]
    
    def __str__(self):
        """Include campus in string representation"""
        base_str = super().__str__() if hasattr(super(), '__str__') else str(self.pk)
        return f"{base_str} ({self.campus.name})"
