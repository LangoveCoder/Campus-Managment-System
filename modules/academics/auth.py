"""
Authorization Facade
Constitution Fix 2

Decouples Academic module from Kernel internals.
Academics never calls kernel authorization services directly.
"""
from typing import Optional
from kernel.exceptions import PermissionDeniedException as PermissionDenied
from kernel.services import AuthorizationService

class AuthorizationFacade:
    @staticmethod
    def require(person_id: Optional[int], campus_id: int, permission_code: str) -> None:
        """
        Enforce permission requirement via Kernel.
        """
        AuthorizationService.require_permission(
            person_id=person_id,
            campus_id=campus_id,
            permission_code=permission_code
        )
