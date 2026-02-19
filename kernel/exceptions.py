"""
Custom Exception Classes for Kernel Module

Provides specific exceptions for identity and authorization errors.
"""


class IdentityException(Exception):
    """Base exception for identity-related errors."""
    pass


class PersonNotFoundException(IdentityException):
    """Raised when a person cannot be found."""
    pass


class DuplicatePersonException(IdentityException):
    """Raised when attempting to create a person with duplicate email/phone."""
    pass


class AuthorizationException(Exception):
    """Base exception for authorization-related errors."""
    pass


class PermissionDeniedException(AuthorizationException):
    """Raised when a permission check fails."""
    
    def __init__(self, person_id, campus_id, permission_code):
        self.person_id = person_id
        self.campus_id = campus_id
        self.permission_code = permission_code
        super().__init__(
            f"Permission denied: Person {person_id} does not have "
            f"'{permission_code}' at campus {campus_id}"
        )


class InvalidBindingException(AuthorizationException):
    """Raised when a role binding is invalid."""
    pass


class BindingExpiredException(AuthorizationException):
    """Raised when attempting to use an expired role binding."""
    pass



class UserAccountNotFoundException(IdentityException):
    """Raised when a user account cannot be found."""
    pass


class BusinessRuleViolation(Exception):
    """Raised when a business rule is violated."""
    pass
