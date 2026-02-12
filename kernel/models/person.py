"""
Person Model - Immutable Human Identity

Represents a unique human being in the system.
"""
import uuid
from django.db import models


class Person(models.Model):
    """
    Represents a unique human being.
    
    This is the ONLY source of truth for human identity.
    One person = one UUID, forever.
    
    Constitution Reference: Section 2.1
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Immutable UUID for this person"
    )
    
    full_name = models.CharField(
        max_length=255,
        help_text="Full legal name"
    )
    
    primary_email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="Primary email address"
    )
    
    primary_phone = models.CharField(
        max_length=20,
        unique=True,
        help_text="Primary phone number with country code"
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Date of birth"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="False if person is no longer associated with institution"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kernel_persons'
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'
        indexes = [
            models.Index(fields=['primary_email'], name='idx_person_email'),
            models.Index(fields=['primary_phone'], name='idx_person_phone'),
        ]
    
    def __str__(self) -> str:
        return f"{self.full_name} ({self.primary_phone})"
    
    def __repr__(self) -> str:
        return f"<Person: {self.full_name}>"
