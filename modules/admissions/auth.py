
from typing import Optional
from kernel.services import AuthorizationService
from kernel.exceptions import PermissionDeniedException

class AuthorizationFacade:
    """
    Decouples Admissions Module from Kernel Authorization Service.
    Enforces strict permission checking as per Constitution.
    """
    
    @staticmethod
    def require(person_id: Optional[int], campus_id: int, permission_code: str) -> None:
        """
        Enforce permission requirement via Kernel.
        
        Args:
            person_id: ID of the person attempting the action (can be None for system actions if allowed)
            campus_id: ID of the campus context
            permission_code: Code of the permission required (e.g., 'admissions.view_applications')
            
        Raises:
            PermissionDenied: If permission is missing.
        """
        if not person_id:
             # System actions usually bypass this, but for user-actions it's critical.
             # If person_id is None, it implies an anonymous request which should generally be denied 
             # for sensitive operations, unless specific logic exists.
             # For now, we enforce person_id for all authorized actions.
             raise PermissionDeniedException(person_id, campus_id, permission_code)

        # Implementation Note: 
        # We prepend 'admissions.' to the code if it's a local permission, 
        # but the AuthorizationService expects 'module.code'.
        # The ADMISSIONS_PERMISSIONS define simple codes like 'view_applications'.
        # So we should pass 'admissions.view_applications'.
        
        full_permission = f"admissions.{permission_code}"
        
        AuthorizationService.require_permission(
            person_id=person_id,
            campus_id=campus_id,
            permission_code=full_permission
        )
