from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.db import models
from django.utils import timezone
from psycopg2.extras import DateTimeTZRange
from .person import Person
from .role import Role
from .campus import Campus


def default_validity():
    """Default validity starting now (open-ended)."""
    return DateTimeTZRange(timezone.now(), None, '[]')


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
    
    # Temporal Validity (PostgreSQL Range Type)
    validity = DateTimeRangeField(
        default=default_validity,
        help_text="Time range validation [start, end)"
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
        constraints = [
            ExclusionConstraint(
                name='exclude_overlapping_role_bindings',
                expressions=[
                    ('person', RangeOperators.EQUAL),
                    ('role', RangeOperators.EQUAL),
                    ('campus', RangeOperators.EQUAL),
                    ('validity', RangeOperators.OVERLAPS),
                ],
                index_type='GIST',
            ),
        ]
        indexes = [
            models.Index(fields=['person', 'campus'], name='idx_binding_person_campus'),
        ]
    
    def __str__(self) -> str:
        return f"{self.person.full_name} as {self.role.name} @ {self.campus.name}"
    
    def __repr__(self) -> str:
        return f"<UserRoleBinding: {self.person.full_name} → {self.role.name} @ {self.campus.name}>"
    
    def save(self, *args, **kwargs):
        """
        Constitutional Rule: Deactivation must close the validity range.
        If is_active is set to False, we cap validity at now.
        """
        if not self.is_active and self.validity and self.validity.upper is None:
            # Close the range at now
            self.validity = DateTimeTZRange(self.validity.lower, timezone.now(), bounds='[)')
        super().save(*args, **kwargs)

    def is_currently_valid(self) -> bool:
        """Check if this binding is currently valid."""
        if not self.is_active:
            return False
        
        # Strictly use the validity range
        if not self.validity:
            return False
            
        return timezone.now() in self.validity
