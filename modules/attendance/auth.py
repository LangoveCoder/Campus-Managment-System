
from typing import Optional
from kernel.services import AuthorizationService
from kernel.exceptions import PermissionDeniedException as PermissionDenied

class AuthorizationFacade:
    """
    Decouples Attendance Module from Kernel Authorization Service.
    Enforces strict permission checking as per Constitution.
    """
    
    @staticmethod
    def require(person_id: Optional[int], campus_id: int, permission_code: str) -> None:
        """
        Enforce permission requirement via Kernel.
        """
        if not person_id:
             raise PermissionDenied(person_id, campus_id, permission_code)

        # Prepend module name to code
        full_permission = f"attendance.{permission_code}"
        
        AuthorizationService.require_permission(
            person_id=person_id,
            campus_id=campus_id,
            permission_code=full_permission
        )
