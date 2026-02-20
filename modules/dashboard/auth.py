from typing import Optional
from kernel.services import AuthorizationService
from kernel.exceptions import PermissionDeniedException as PermissionDenied


class AuthorizationFacade:
    """
    Dashboard Authorization Facade.

    Unlike module facades (academics, attendance, workforce), this does NOT
    prepend a module name prefix. The dashboard is a cross-module consumer —
    it enforces permissions that belong to other modules (e.g. 'academics.view_program').
    It passes full permission codes directly to the kernel.
    """

    @staticmethod
    def require(person_id: Optional[int], campus_id: int, full_permission_code: str) -> None:
        if not person_id:
            raise PermissionDenied(None, campus_id, full_permission_code)

        AuthorizationService.require_permission(
            person_id=person_id,
            campus_id=campus_id,
            permission_code=full_permission_code,
        )
