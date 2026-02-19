from typing import Optional
from kernel.services import AuthorizationService
from kernel.exceptions import PermissionDeniedException as PermissionDenied

class AuthorizationFacade:
    """
    Decouples Workforce Module from Kernel Authorization Service.
    """
    
    @staticmethod
    def require(person_id: Optional[int], campus_id: int, permission_code: str) -> None:
        if not person_id:
             raise PermissionDenied("Authentication required.")

        full_permission = f"workforce.{permission_code}"
        
        AuthorizationService.require_permission(
            person_id=person_id,
            campus_id=campus_id,
            permission_code=full_permission
        )
