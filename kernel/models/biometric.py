"""
BiometricIdentity Model - Biometric Data Storage

Stores biometric enrollment data for persons.
"""
from django.db import models
from .person import Person


class BiometricIdentity(models.Model):
    """
    Stores biometric enrollment data.
    
    Used for attendance and identity verification.
    
    Constitution Reference: Section 2.8
    """
    
    BIOMETRIC_TYPE_CHOICES = [
        ('FINGERPRINT', 'Fingerprint'),
        ('FACE', 'Face Recognition'),
        ('IRIS', 'Iris Scan'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='biometric_identities',
        help_text="The person this biometric belongs to"
    )
    
    biometric_type = models.CharField(
        max_length=20,
        choices=BIOMETRIC_TYPE_CHOICES,
        help_text="Type of biometric data"
    )
    
    encoding = models.BinaryField(
        help_text="Encrypted biometric template/encoding"
    )
    
    quality_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Quality score of the biometric sample (0-100)"
    )
    
    enrollment_device_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="ID of device used for enrollment"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this biometric is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'kernel_biometric_identities'
        verbose_name = 'Biometric Identity'
        verbose_name_plural = 'Biometric Identities'
        indexes = [
            models.Index(fields=['person', 'biometric_type'], name='idx_biometric_person_type'),
        ]
    
    def __str__(self) -> str:
        return f"{self.person.full_name} - {self.get_biometric_type_display()}"
    
    def __repr__(self) -> str:
        return f"<BiometricIdentity: {self.person.full_name} - {self.biometric_type}>"
