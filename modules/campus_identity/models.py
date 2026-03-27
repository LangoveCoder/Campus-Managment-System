"""
Campus Identity Models

CampusIDConfig  — per-campus ID generation settings (prefix, padding, sequence)
CampusPerson    — assigns a permanent campus identifier to a person
"""
import uuid as _uuid
from django.db import models


class CampusIDConfig(models.Model):
    """Per-campus configuration for identifier generation."""
    campus_id = models.IntegerField(unique=True)
    prefix = models.CharField(max_length=20, blank=True, default='',
                              help_text="Optional prefix, e.g. 'GCQ'. Leave blank for numeric-only IDs.")
    padding = models.PositiveIntegerField(default=6,
                                          help_text="Zero-pad width for the sequence number.")
    current_sequence = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'campus_identity'

    def __str__(self):
        return f"IDConfig[campus={self.campus_id}, prefix={self.prefix!r}, seq={self.current_sequence}]"


class CampusPerson(models.Model):
    """Assigns a permanent, immutable campus identifier to a person."""
    id = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    campus_id = models.IntegerField(db_index=True)
    person = models.ForeignKey(
        'kernel.Person',
        on_delete=models.PROTECT,
        related_name='campus_memberships',
    )
    campus_identifier = models.CharField(
        max_length=20,
        help_text="Permanent campus ID, e.g. GCQ-000001. Immutable once set."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'campus_identity'
        unique_together = [
            ('campus_id', 'person'),
            ('campus_id', 'campus_identifier'),
        ]

    def __str__(self):
        return f"{self.campus_identifier} — {self.person}"
