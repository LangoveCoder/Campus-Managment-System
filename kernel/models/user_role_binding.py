"""
UserRoleBinding Model - The Heart of Authorization

Binds a person to a role at a specific campus for a time period.
"""
from django.db import models
from django.utils import timezone
from .person import Person
from .role import Role
from .campus import Campus


class UserRoleBinding(models.Model):
    """
    Binds a person to a role at a campus.
    
    This is THE authorization table.
    
    Constitution Reference: Section 2.7
    """
    
    id = models.BigAutoField(primary_key=True)
    
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='role_bindings',
        help_text="The person"
    )
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_bindings',
        help_text="The role"
    )
    
    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        related_name='user_bindings',
        help_text="The campus where this role applies"
    )
    
    valid_from = models.DateTimeField(
        help_text="Role is valid from this date"
    )
    
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Role is valid until this date (null = indefinite)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this binding is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'kernel_user_role_bindings'
        verbose_name = 'User Role Binding'
        verbose_name_plural = 'User Role Bindings'
        indexes = [
            models.Index(fields=['person', 'campus'], name='idx_binding_person_campus'),
            models.Index(fields=['valid_from', 'valid_until'], name='idx_binding_validity'),
        ]
        unique_together = [['person', 'role', 'campus', 'valid_from']]
    
    def __str__(self) -> str:
        return f"{self.person.full_name} as {self.role.name} @ {self.campus.name}"
    
    def __repr__(self) -> str:
        return f"<UserRoleBinding: {self.person.full_name} → {self.role.name} @ {self.campus.name}>"
    
    def is_currently_valid(self) -> bool:
        """Check if this binding is currently valid."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        return True
