from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class AuditLog(models.Model):
    """
    Immutable audit log for tracking all system actions.
    
    This model records WHO did WHAT, WHERE, WHEN, and WHY.
    It is designed to be append-only and immutable.
    """
    
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # WHO (The Actor)
    actor = models.ForeignKey(
        'kernel.Person',
        on_delete=models.PROTECT, # Never delete audit logs even if person is deleted
        related_name='audit_logs',
        null=True, # Null for system actions or anonymous users
        blank=True,
        help_text=_("The person who performed the action")
    )
    
    # WHERE (Context)
    campus = models.ForeignKey(
        'kernel.Campus',
        on_delete=models.PROTECT,
        related_name='audit_logs',
        null=True, # Null for global actions
        blank=True,
        help_text=_("The campus where the action occurred")
    )
    
    role = models.ForeignKey(
        'kernel.Role',
        on_delete=models.PROTECT,
        related_name='audit_logs',
        null=True,
        blank=True,
        help_text=_("The role assumed by the actor")
    )
    
    # WHAT (Action & Target)
    action = models.CharField(
        max_length=255,
        db_index=True,
        help_text=_("Name of the action (e.g., 'create_student', 'login_attempt')")
    )
    
    target_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Type of the target entity (e.g., 'Student', 'Course')")
    )
    
    target_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("ID of the target entity")
    )
    
    # CHANGES (State)
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text=_("JSON delta of changes (e.g., {'old': ..., 'new': ...})")
    )
    
    # METADATA
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        unpack_ipv4=True
    )
    
    user_agent = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )
    
    # WHEN
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    # RESULT
    RESULT_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('DENIED', 'Denied'),
    ]
    
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default='SUCCESS',
        db_index=True
    )
    
    reason = models.TextField(
        null=True,
        blank=True,
        help_text=_("Reason for failure or denial")
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        indexes = [
            models.Index(fields=['actor', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['campus', 'timestamp']),
            models.Index(fields=['target_type', 'target_id']),
        ]

    def __str__(self):
        actor_name = self.actor.full_name if self.actor else "System"
        return f"{self.timestamp} - {actor_name} - {self.action} ({self.result})"
