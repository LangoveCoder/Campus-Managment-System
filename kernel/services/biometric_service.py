"""
Biometric Service

Handles all biometric operations: enrollment, authentication, and quality checks.
"""
from typing import Optional, Dict, Any, Tuple
from django.db import transaction
from django.utils import timezone
from kernel.models import Person, BiometricIdentity, Device
from .audit_service import AuditService
from ..decorators import audit_action

class BiometricService:
    @staticmethod
    def verify_quality(biometric_data: bytes) -> float:
        """
        Mock quality check.
        In production, this would use an SDK to analyze the image/template.
        Returns a score between 0.0 and 1.0.
        """
        # Mock logic: length of data determines quality for now
        if not biometric_data:
            return 0.0
        return 0.95  # Mock high quality

    @staticmethod
    @audit_action(action="enroll_biometric", target_type="Person")
    def enroll_biometric(
        person_id: str,
        biometric_type: str,
        biometric_data: bytes,
        device_id: Optional[str] = None
    ) -> BiometricIdentity:
        """
        Enrolls a new biometric identity for a person.
        Enciphers and stores the template.
        """
        try:
            person = Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            raise ValueError(f"Person with ID {person_id} does not exist.")

        # Validate quality
        quality_score = BiometricService.verify_quality(biometric_data)
        if quality_score < 0.6:
            raise ValueError("Biometric data quality is too low (minimum 0.6 required).")

        # Check existing enrollment (prevent duplicates if needed, or allow multi)
        # For now, we allow multiple fingers/faces.

        enrollment_device_id = None
        if device_id:
            try:
                device = Device.objects.get(id=device_id)
                enrollment_device_id = str(device.id)
                # Update device heartbeat/usage?
            except Device.DoesNotExist:
                pass # Log warning, but proceed or fail? Proceed for now.

        # Encrypt data (Mock encryption for now, just storing raw bytes as 'encrypted')
        # In production: use proper crypto (e.g. Fernet)
        encrypted_data = biometric_data 

        biometric = BiometricIdentity.objects.create(
            person=person,
            biometric_type=biometric_type,
            encoding=encrypted_data,
            quality_score=quality_score * 100, # Store as 0-100
            enrollment_device_id=enrollment_device_id,
            is_active=True
        )
        
        return biometric

    @staticmethod
    @audit_action(action="authenticate_biometric", target_type="Person")
    def authenticate_biometric(
        biometric_type: str,
        biometric_data: bytes
    ) -> Optional[Person]:
        """
        Authenticates a person using biometric data.
        Returns the Person object if match found, else None.
        Matches 1:N against all active identities of that type.
        """
        # 1. Get all active encodings of this type
        candidates = BiometricIdentity.objects.filter(
            biometric_type=biometric_type,
            is_active=True
        ).select_related('person')

        # 2. Iterate and match (Mock matching)
        for candidate in candidates:
            # Mock match: Exact byte match
            if candidate.encoding == biometric_data:
                return candidate.person
            
        return None
