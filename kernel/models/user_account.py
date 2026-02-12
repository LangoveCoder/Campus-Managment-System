"""
UserAccount Model - Authentication Shell

Represents login credentials for a Person.
"""
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from .person import Person


class UserAccountManager(UserManager):
    """Custom manager for UserAccount model."""
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create superuser with auto-created Person."""
        person = Person.objects.create(
            full_name=f"Superuser {username}",
            primary_phone=f"+00-{username[:10]}"
        )
        
        extra_fields.setdefault('person', person)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return super().create_superuser(username, email, password, **extra_fields)


class UserAccount(AbstractUser):
    """
    Represents login credentials.
    
    Authentication ≠ Authorization.
    UserAccount contains NO role or campus logic.
    
    Constitution Reference: Section 2.2
    """
    
    id = models.BigAutoField(primary_key=True)
    
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='user_accounts',
        null=True,
        blank=True,
        help_text="The person this account belongs to"
    )
    
    is_locked = models.BooleanField(
        default=False,
        help_text="True if account is locked"
    )
    
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Failed login count"
    )
    
    lockout_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Locked until this time"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserAccountManager()
    
    class Meta:
        db_table = 'kernel_user_accounts'
        verbose_name = 'User Account'
        verbose_name_plural = 'User Accounts'
        indexes = [
            models.Index(fields=['username'], name='idx_useraccount_username'),
            models.Index(fields=['email'], name='idx_useraccount_email'),
        ]
    
    def __str__(self) -> str:
        if self.person:
            return f"{self.username} ({self.person.full_name})"
        return self.username
    
    def __repr__(self) -> str:
        return f"<UserAccount: {self.username}>"
