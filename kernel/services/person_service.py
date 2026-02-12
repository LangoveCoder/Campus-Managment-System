"""
Person Service - Business Logic for Person Operations

Higher-level business logic built on top of IdentityService.
"""
from typing import List, Optional
from uuid import UUID
from django.db.models import QuerySet, Q
from ..models import Person, Role, Campus
from .identity_service import IdentityService
from .role_binding_service import RoleBindingService


class PersonService:
    """
    Service for person-related business logic.
    
    Provides higher-level operations built on IdentityService.
    """
    
    @staticmethod
    def register_new_person(
        full_name: str,
        primary_phone: str,
        primary_email: Optional[str] = None,
        **kwargs
    ) -> Person:
        """
        Register a new person in the system.
        
        This is a convenience wrapper around IdentityService.create_person
        with additional business logic if needed.
        
        Args:
            full_name: Full legal name
            primary_phone: Primary phone number
            primary_email: Primary email address (optional)
            **kwargs: Additional fields
            
        Returns:
            Created Person object
        """
        return IdentityService.create_person(
            full_name=full_name,
            primary_phone=primary_phone,
            primary_email=primary_email,
            **kwargs
        )
    
    @staticmethod
    def search_persons(query: str, campus_id: Optional[int] = None) -> QuerySet[Person]:
        """
        Search for persons by name, email, or phone.
        
        Args:
            query: Search query string
            campus_id: Optional campus ID to filter by
            
        Returns:
            QuerySet of matching Person objects
        """
        # Search by name, email, or phone
        queryset = Person.objects.filter(
            Q(full_name__icontains=query) |
            Q(primary_email__icontains=query) |
            Q(primary_phone__icontains=query)
        ).filter(is_active=True)
        
        # If campus_id is provided, filter by persons who have bindings at that campus
        if campus_id:
            from ..models import UserRoleBinding
            person_ids = UserRoleBinding.objects.filter(
                campus_id=campus_id,
                is_active=True
            ).values_list('person_id', flat=True).distinct()
            
            queryset = queryset.filter(id__in=person_ids)
        
        return queryset
    
    @staticmethod
    def get_person_roles(person_id: UUID, campus_id: Optional[int] = None) -> List[Role]:
        """
        Get all roles for a person, optionally filtered by campus.
        
        Args:
            person_id: UUID of the person
            campus_id: Optional campus ID to filter by
            
        Returns:
            List of Role objects
        """
        bindings = RoleBindingService.get_bindings_for_person(
            person_id=person_id,
            active_only=True
        )
        
        if campus_id:
            bindings = bindings.filter(campus_id=campus_id)
        
        role_ids = bindings.values_list('role_id', flat=True).distinct()
        return list(Role.objects.filter(id__in=role_ids))
    
    @staticmethod
    def get_person_campuses(person_id: UUID) -> List[Campus]:
        """
        Get all campuses where a person has active role bindings.
        
        Args:
            person_id: UUID of the person
            
        Returns:
            List of Campus objects
        """
        bindings = RoleBindingService.get_bindings_for_person(
            person_id=person_id,
            active_only=True
        )
        
        campus_ids = bindings.values_list('campus_id', flat=True).distinct()
        return list(Campus.objects.filter(id__in=campus_ids))
    
    @staticmethod
    def get_person_summary(person_id: UUID) -> dict:
        """
        Get a summary of a person's information including roles and campuses.
        
        Args:
            person_id: UUID of the person
            
        Returns:
            Dictionary with person summary
        """
        person = IdentityService.get_person_by_id(person_id)
        roles = PersonService.get_person_roles(person_id)
        campuses = PersonService.get_person_campuses(person_id)
        
        return {
            'person': person,
            'roles': roles,
            'campuses': campuses,
            'total_bindings': RoleBindingService.get_bindings_for_person(
                person_id, active_only=True
            ).count()
        }
