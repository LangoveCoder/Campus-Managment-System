"""
Device Model

Tracks hardware devices used for biometric enrollment and authentication.
"""
from django.db import models
import uuid
from .campus import Campus

class Device(models.Model):
    """
    Represents a physical biometric scanner/camera.
    """
    DEVICE_TYPE_CHOICES = [
        ('FINGERPRINT_READER', 'Fingerprint Reader'),
        ('FACE_CAM', 'Facial Recognition Camera'),
        ('IRIS_SCANNER', 'Iris Scanner'),
    ]

    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('ERROR', 'Error State'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Friendly name for the device")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='devices')
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    driver_identifier = models.CharField(
        max_length=100, 
        help_text="Hardware ID or Serial Number used by the driver"
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OFFLINE')
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kernel_devices'
        verbose_name = 'Biometric Device'
        verbose_name_plural = 'Biometric Devices'
        indexes = [
            models.Index(fields=['campus', 'device_type']),
            models.Index(fields=['driver_identifier']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()})"
