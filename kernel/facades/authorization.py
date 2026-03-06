"""
Authorization Facade - System-Wide Access Control

Unified entry point for all system modules to perform permission checks,
decoupling them from internal Kernel services in accordance with Constitutional Architecture.
"""
from typing import Optional
from kernel.services import AuthorizationService
from kernel.exceptions import PermissionDeniedException as PermissionDenied

class AuthorizationFacade:
    @staticmethod
    def require(person_id: Optional[str|int], campus_id: str|int, permission_code: str) -> None:
        """
        Enforce permission requirement via Kernel.
        
        Args:
            person_id: The ID of the person making the request
            campus_id: The ID of the campus context
            permission_code: Fully qualified permission code (e.g. 'workforce.manage_devices')
            
        Raises:
            PermissionDenied: If the person lacks the required permission
        """
        if not person_id:
            raise PermissionDenied(person_id, campus_id, permission_code)

        AuthorizationService.require_permission(
            person_id=person_id,
            campus_id=campus_id,
            permission_code=permission_code
        )
