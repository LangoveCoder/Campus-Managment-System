
from django.db import models
from django.utils.translation import gettext_lazy as _
from kernel.models.base import BaseCampusModel
import uuid

class WorkforceAttendanceDevice(BaseCampusModel):
    """
    Physical biometric reader device.
    Authenticated via API Token (hashed in real-world, here plain for simplicity/prototype or hashed if required).
    Prompt says "API token per device".
    """
    class DeviceType(models.TextChoices):
        FINGERPRINT = 'FINGERPRINT', _('Fingerprint')
        FACE = 'FACE', _('Face')
        HYBRID = 'HYBRID', _('Hybrid')

    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    api_token = models.CharField(max_length=64, unique=True, help_text="Secret token for device authentication")
    
    is_active = models.BooleanField(default=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.device_type})"
