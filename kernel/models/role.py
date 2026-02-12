"""
Role Model - Named Responsibility

Represents a named role that can be assigned to users.
"""
from django.db import models


class Role(models.Model):
    """
    Represents a named role.
    
    Roles are containers for permissions.
    
    Constitution Reference: Section 2.4
    """
    
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('CAMPUS_ADMIN', 'Campus Admin'),
        ('REGISTRAR', 'Registrar'),
        ('FACULTY', 'Faculty'),
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent'),
        ('ACCOUNTANT', 'Accountant'),
        ('LIBRARIAN', 'Librarian'),
        ('SECURITY', 'Security'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    
    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        help_text="Role name"
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Role description"
    )
    
    is_system_role = models.BooleanField(
        default=True,
        help_text="True if this is a predefined system role"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'kernel_roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self) -> str:
        return self.get_name_display()
    
    def __repr__(self) -> str:
        return f"<Role: {self.name}>"
