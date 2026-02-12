"""
Permission Model - Atomic Capability

Represents a single atomic permission/capability.
"""
from django.db import models


class Permission(models.Model):
    """
    Represents an atomic permission.
    
    Permissions are the smallest unit of access control.
    
    Constitution Reference: Section 2.5
    """
    
    id = models.BigAutoField(primary_key=True)
    
    code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique permission code (e.g., 'kernel.view_person')"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Human-readable permission name"
    )
    
    module = models.CharField(
        max_length=50,
        help_text="Module this permission belongs to (e.g., 'kernel', 'academics')"
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed description of what this permission allows"
    )
    
    is_dangerous = models.BooleanField(
        default=False,
        help_text="True if this permission grants destructive capabilities"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'kernel_permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        indexes = [
            models.Index(fields=['module'], name='idx_permission_module'),
        ]
    
    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
    
    def __repr__(self) -> str:
        return f"<Permission: {self.code}>"
