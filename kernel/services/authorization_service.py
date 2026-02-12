"""
Authorization Service - Permission Checking and Role Management

Handles all authorization logic including permission checks and role binding queries.
"""
from typing import Set
from uuid import UUID
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from ..models import UserRoleBinding, RolePermissionMap, Permission
from ..exceptions import PermissionDeniedException


class AuthorizationService:
    """
    Service for authorization and permission checking.
    
    All permission checks should go through this service.
    """
    
    @staticmethod
    def get_active_bindings(person_id: UUID, campus_id: int) -> QuerySet[UserRoleBinding]:
        """
        Get all active role bindings for a person at a specific campus.
        
        Args:
            person_id: UUID of the person
            campus_id: ID of the campus
            
        Returns:
            QuerySet of active UserRoleBinding objects
        """
        now = timezone.now()
        
        return UserRoleBinding.objects.filter(
            person_id=person_id,
            campus_id=campus_id,
            is_active=True,
            valid_from__lte=now
        ).filter(
            # valid_until is null (indefinite) OR valid_until is in the future
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now)
        ).select_related('role', 'campus')
    
    @staticmethod
    def get_all_permissions(person_id: UUID, campus_id: int) -> Set[str]:
        """
        Get all permission codes for a person at a specific campus.
        
        Aggregates permissions from all active role bindings.
        
        Args:
            person_id: UUID of the person
            campus_id: ID of the campus
            
        Returns:
            Set of permission codes (e.g., {'kernel.view_person', 'kernel.add_person'})
        """
        # Get all active bindings
        bindings = AuthorizationService.get_active_bindings(person_id, campus_id)
        
        if not bindings.exists():
            return set()
        
        # Get all role IDs from active bindings
        role_ids = bindings.values_list('role_id', flat=True)
        
        # Get all permissions for these roles
        permission_codes = RolePermissionMap.objects.filter(
            role_id__in=role_ids
        ).select_related('permission').values_list('permission__code', flat=True)
        
        return set(permission_codes)
    
    @staticmethod
    def has_permission(person_id: UUID, campus_id: int, permission_code: str) -> bool:
        """
        Check if a person has a specific permission at a campus.
        
        Args:
            person_id: UUID of the person
            campus_id: ID of the campus
            permission_code: Permission code to check (e.g., 'kernel.view_person')
            
        Returns:
            True if person has the permission, False otherwise
        """
        from .audit_service import AuditService
        
        all_permissions = AuthorizationService.get_all_permissions(person_id, campus_id)
        has_perm = permission_code in all_permissions
        
        # Log the check
        # We only log failures by default to avoid spam, 
        # unless it's a critical permission
        if not has_perm:
             AuditService.log_permission_check(
                person_id=person_id,
                campus_id=campus_id,
                permission=permission_code,
                granted=False
            )
            
        return has_perm
    
    @staticmethod
    def require_permission(person_id: UUID, campus_id: int, permission_code: str) -> None:
        """
        Require a permission, raising an exception if not granted.
        
        Args:
            person_id: UUID of the person
            campus_id: ID of the campus
            permission_code: Permission code to require
            
        Raises:
            PermissionDeniedException: If person doesn't have the permission
        """
        if not AuthorizationService.has_permission(person_id, campus_id, permission_code):
            raise PermissionDeniedException(person_id, campus_id, permission_code)
    
    @staticmethod
    def can_access_entity(
        person_id: UUID,
        campus_id: int,
        entity_type: str,
        entity_id: int
    ) -> bool:
        """
        Check if a person can access a specific entity.
        
        This is for future entity-level scoping (e.g., teacher can only access their classes).
        Currently returns True if person has any active binding at the campus.
        
        Args:
            person_id: UUID of the person
            campus_id: ID of the campus
            entity_type: Type of entity (e.g., 'class', 'department')
            entity_id: ID of the specific entity
            
        Returns:
            True if person can access the entity, False otherwise
        """
        # For now, just check if person has any active binding at campus
        # In Phase 3, we'll add entity_type and entity_id to UserRoleBinding
        bindings = AuthorizationService.get_active_bindings(person_id, campus_id)
        return bindings.exists()
    
    @staticmethod
    def get_person_roles_at_campus(person_id: UUID, campus_id: int) -> QuerySet:
        """
        Get all roles a person has at a specific campus.
        
        Args:
            person_id: UUID of the person
            campus_id: ID of the campus
            
        Returns:
            QuerySet of Role objects
        """
        from ..models import Role
        
        bindings = AuthorizationService.get_active_bindings(person_id, campus_id)
        role_ids = bindings.values_list('role_id', flat=True)
        
        return Role.objects.filter(id__in=role_ids)
