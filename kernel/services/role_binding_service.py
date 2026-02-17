"""
Role Binding Service - Role Assignment Management

Handles creation, deactivation, and queries for user role bindings.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from psycopg2.extras import DateTimeTZRange
from ..models import UserRoleBinding, Person, Role, Campus
from ..exceptions import InvalidBindingException, BindingExpiredException
from .identity_service import IdentityService


class RoleBindingService:
    """
    Service for managing user role bindings.
    
    All role binding operations should go through this service.
    """
    
    @staticmethod
    def create_binding(
        person_id: UUID,
        role_id: int,
        campus_id: int,
        valid_from: datetime,
        valid_until: Optional[datetime] = None,
        **kwargs
    ) -> UserRoleBinding:
        """
        Create a new role binding for a person.
        
        Args:
            person_id: UUID of the person
            role_id: ID of the role
            campus_id: ID of the campus
            valid_from: Start date/time for the binding
            valid_until: End date/time for the binding (None = indefinite)
            **kwargs: Additional fields
            
        Returns:
            Created UserRoleBinding object
            
        Raises:
            InvalidBindingException: If binding parameters are invalid
        """
        # Validate that person exists
        person = IdentityService.get_person_by_id(person_id)
        
        # Validate that role exists
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise InvalidBindingException(f"Role with ID {role_id} not found")
        
        # Validate that campus exists
        try:
            campus = Campus.objects.get(id=campus_id)
        except Campus.DoesNotExist:
            raise InvalidBindingException(f"Campus with ID {campus_id} not found")
        
        # Validate date range
        if valid_until and valid_until <= valid_from:
            raise InvalidBindingException(
                "valid_until must be after valid_from"
            )
        
        # Create the binding
        # Convert valid_from/until to PostgreSQL Range
        validity = DateTimeTZRange(valid_from, valid_until, bounds='[)')
        
        binding = UserRoleBinding.objects.create(
            person=person,
            role=role,
            campus=campus,
            validity=validity,
            is_active=True,
            **kwargs
        )
        
        return binding
    
    @staticmethod
    def deactivate_binding(binding_id: int) -> None:
        """
        Deactivate a role binding.
        
        Args:
            binding_id: ID of the binding to deactivate
            
        Raises:
            InvalidBindingException: If binding doesn't exist
        """
        try:
            binding = UserRoleBinding.objects.get(id=binding_id)
            binding.is_active = False
            binding.deactivated_at = timezone.now()
            binding.save()
        except UserRoleBinding.DoesNotExist:
            raise InvalidBindingException(f"Binding with ID {binding_id} not found")
    
    @staticmethod
    def get_bindings_for_person(
        person_id: UUID,
        active_only: bool = True
    ) -> QuerySet[UserRoleBinding]:
        """
        Get all role bindings for a person.
        
        Args:
            person_id: UUID of the person
            active_only: If True, only return active bindings
            
        Returns:
            QuerySet of UserRoleBinding objects
        """
        queryset = UserRoleBinding.objects.filter(
            person_id=person_id
        ).select_related('role', 'campus')
        
        if active_only:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                validity__contains=now
            )
        
        return queryset
    
    @staticmethod
    def get_bindings_for_campus(
        campus_id: int,
        active_only: bool = True
    ) -> QuerySet[UserRoleBinding]:
        """
        Get all role bindings for a campus.
        
        Args:
            campus_id: ID of the campus
            active_only: If True, only return active bindings
            
        Returns:
            QuerySet of UserRoleBinding objects
        """
        queryset = UserRoleBinding.objects.filter(
            campus_id=campus_id
        ).select_related('person', 'role')
        
        if active_only:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                validity__contains=now
            )
        
        return queryset
    
    @staticmethod
    def is_binding_valid(binding_id: int) -> bool:
        """
        Check if a binding is currently valid.
        
        Args:
            binding_id: ID of the binding to check
            
        Returns:
            True if binding is valid, False otherwise
        """
        try:
            binding = UserRoleBinding.objects.get(id=binding_id)
            return binding.is_currently_valid()
        except UserRoleBinding.DoesNotExist:
            return False
    
    @staticmethod
    def extend_binding(binding_id: int, new_valid_until: datetime) -> UserRoleBinding:
        """
        Extend the validity period of a binding.
        
        Args:
            binding_id: ID of the binding to extend
            new_valid_until: New end date/time
            
        Returns:
            Updated UserRoleBinding object
            
        Raises:
            InvalidBindingException: If binding doesn't exist or new date is invalid
        """
        try:
            binding = UserRoleBinding.objects.get(id=binding_id)
        except UserRoleBinding.DoesNotExist:
            raise InvalidBindingException(f"Binding with ID {binding_id} not found")
        
        if new_valid_until <= binding.valid_from:
            raise InvalidBindingException(
                "new_valid_until must be after valid_from"
            )
        
        # Create new range preserving the start
        current_start = binding.validity.lower
        binding.validity = DateTimeTZRange(current_start, new_valid_until, bounds='[)')
        binding.save()
        
        return binding
    
    @staticmethod
    def activate_binding(binding_id: int) -> None:
        """
        Reactivate a previously deactivated binding.
        
        Args:
            binding_id: ID of the binding to activate
            
        Raises:
            InvalidBindingException: If binding doesn't exist
        """
        try:
            binding = UserRoleBinding.objects.get(id=binding_id)
            binding.is_active = True
            binding.deactivated_at = None
            binding.save()
        except UserRoleBinding.DoesNotExist:
            raise InvalidBindingException(f"Binding with ID {binding_id} not found")
