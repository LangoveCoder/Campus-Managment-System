import hashlib
from modules.workforce.models import WorkforceAttendanceDevice
from kernel.exceptions import PermissionDeniedException as PermissionDenied, BusinessRuleViolation
from modules.workforce.auth import AuthorizationFacade

class DeviceRegistrationService:
    @staticmethod
    def register_device(person_id: int, campus_id: int, name: str, device_type: str, ip_address: str = None) -> tuple[WorkforceAttendanceDevice, str]:
        """
        Registers a new biometric device and returns (device, plain_text_token).
        The token is shown ONCE and then hashed.
        """
        AuthorizationFacade.require(person_id, campus_id, 'manage_devices')
        
        # Generate API Token
        plain_token = secrets.token_urlsafe(32)
        # In a real system, we would hash this.
        # For this v1 prototype, we store it plainly as per the model definition
        # "api_token = models.CharField(max_length=64, unique=True, help_text="Secret token for device authentication")"
        # However, the prompt says "api_token (hashed)". Let's simulate hashing or store plain if hashing lib not strictly enforced.
        # Let's keep it simple: Store plain for now to ensure prototype works easily, or a simple hash.
        # Decisions: Store plain for v1 to avoid "authentication failed" loops during debugging, 
        # unless prompt strictly enforced "hashed". Prompt: "api_token (hashed)". Okay, we must hash.
        
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        
        device = WorkforceAttendanceDevice.objects.create(
            campus_id=campus_id,
            name=name,
            device_type=device_type,
            ip_address=ip_address,
            api_token=token_hash,
            is_active=True
        )
        
        return device, plain_token

    @staticmethod
    def rotate_token(person_id: int, campus_id: int, device_id: int) -> str:
        AuthorizationFacade.require(person_id, campus_id, 'manage_devices')
        device = WorkforceAttendanceDevice.objects.get(id=device_id, campus_id=campus_id)
        
        plain_token = secrets.token_urlsafe(32)
        device.api_token = hashlib.sha256(plain_token.encode()).hexdigest()
        device.save()
        
        return plain_token
