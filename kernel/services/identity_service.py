"""
Identity Service - Person Identity Management

Handles all operations related to person identity resolution and management.
"""
from typing import Optional
from uuid import UUID
from django.db import IntegrityError
from ..models import Person, UserAccount
from ..exceptions import (
    PersonNotFoundException,
    DuplicatePersonException,
    UserAccountNotFoundException
)
from ..decorators import audit_action


class IdentityService:
    """
    Service for managing person identities.
    
    All person-related queries should go through this service.
    """
    
    @staticmethod
    def get_person_by_id(person_id: UUID) -> Person:
        """
        Get a person by their UUID.
        
        Args:
            person_id: UUID of the person
            
        Returns:
            Person object
            
        Raises:
            PersonNotFoundException: If person doesn't exist
        """
        try:
            return Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            raise PersonNotFoundException(f"Person with ID {person_id} not found")
    
    @staticmethod
    def get_person_by_email(email: str) -> Optional[Person]:
        """
        Get a person by their email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Person object or None if not found
        """
        try:
            return Person.objects.get(primary_email=email)
        except Person.DoesNotExist:
            return None
    
    @staticmethod
    def get_person_by_phone(phone: str) -> Optional[Person]:
        """
        Get a person by their phone number.
        
        Args:
            phone: Phone number to search for
            
        Returns:
            Person object or None if not found
        """
        try:
            return Person.objects.get(primary_phone=phone)
        except Person.DoesNotExist:
            return None
    
    @staticmethod
    def get_person_from_user_account(user_account: UserAccount) -> Person:
        """
        Get the person associated with a user account.
        
        Args:
            user_account: UserAccount object
            
        Returns:
            Person object
            
        Raises:
            PersonNotFoundException: If user account has no associated person
        """
        if not user_account.person:
            raise PersonNotFoundException(
                f"UserAccount {user_account.username} has no associated person"
            )
        return user_account.person
    
    @staticmethod
    @audit_action(action_name="create_person")
    def create_person(
        full_name: str,
        primary_phone: str,
        primary_email: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        **kwargs
    ) -> Person:
        """
        Create a new person.
        
        Args:
            full_name: Full legal name
            primary_phone: Primary phone number (must be unique)
            primary_email: Primary email address (optional, must be unique if provided)
            date_of_birth: Date of birth (optional)
            **kwargs: Additional fields
            
        Returns:
            Created Person object
            
        Raises:
            DuplicatePersonException: If email or phone already exists
        """
        try:
            person = Person.objects.create(
                full_name=full_name,
                primary_phone=primary_phone,
                primary_email=primary_email,
                date_of_birth=date_of_birth,
                **kwargs
            )
            return person
        except IntegrityError as e:
            if 'primary_email' in str(e):
                raise DuplicatePersonException(f"Email {primary_email} already exists")
            elif 'primary_phone' in str(e):
                raise DuplicatePersonException(f"Phone {primary_phone} already exists")
            raise
    
    @staticmethod
    @audit_action(action_name="update_person")
    def update_person(person_id: UUID, **kwargs) -> Person:
        """
        Update a person's information.
        
        Args:
            person_id: UUID of the person to update
            **kwargs: Fields to update
            
        Returns:
            Updated Person object
            
        Raises:
            PersonNotFoundException: If person doesn't exist
            DuplicatePersonException: If update would create duplicate email/phone
        """
        person = IdentityService.get_person_by_id(person_id)
        
        try:
            for key, value in kwargs.items():
                setattr(person, key, value)
            person.save()
            return person
        except IntegrityError as e:
            if 'primary_email' in str(e):
                raise DuplicatePersonException(
                    f"Email {kwargs.get('primary_email')} already exists"
                )
            elif 'primary_phone' in str(e):
                raise DuplicatePersonException(
                    f"Phone {kwargs.get('primary_phone')} already exists"
                )
            raise
    
    @staticmethod
    @audit_action(action_name="deactivate_person")
    def deactivate_person(person_id: UUID) -> None:
        """
        Deactivate a person (soft delete).
        
        Args:
            person_id: UUID of the person to deactivate
            
        Raises:
            PersonNotFoundException: If person doesn't exist
        """
        person = IdentityService.get_person_by_id(person_id)
        person.is_active = False
        person.save()
    
    @staticmethod
    @audit_action(action_name="activate_person")
    def activate_person(person_id: UUID) -> None:
        """
        Reactivate a previously deactivated person.
        
        Args:
            person_id: UUID of the person to activate
            
        Raises:
            PersonNotFoundException: If person doesn't exist
        """
        person = IdentityService.get_person_by_id(person_id)
        person.is_active = True
        person.save()
