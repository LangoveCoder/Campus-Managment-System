"""
Campus Model - Physical/Logical Location

Represents a campus or location where operations occur.
"""
from django.db import models


class Campus(models.Model):
    """
    Represents a physical or logical campus.
    
    Used for data isolation and role scoping.
    
    Constitution Reference: Section 2.3
    """
    
    CAMPUS_TYPE_CHOICES = [
        ('PHYSICAL', 'Physical Campus'),
        ('VIRTUAL', 'Virtual Campus'),
        ('DEPARTMENT', 'Department'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Campus name"
    )
    
    campus_type = models.CharField(
        max_length=20,
        choices=CAMPUS_TYPE_CHOICES,
        default='PHYSICAL',
        help_text="Type of campus"
    )
    
    address = models.TextField(
        null=True,
        blank=True,
        help_text="Physical address if applicable"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this campus is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'kernel_campuses'
        verbose_name = 'Campus'
        verbose_name_plural = 'Campuses'
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"<Campus: {self.name}>"
