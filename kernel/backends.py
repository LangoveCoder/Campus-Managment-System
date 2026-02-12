"""
Custom Authentication Backend for UserAccount Model
"""
from django.contrib.auth.backends import ModelBackend
from kernel.models import UserAccount


class UserAccountBackend(ModelBackend):
    """
    Custom authentication backend for UserAccount model.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate using username and password."""
        try:
            user = UserAccount.objects.get(username=username)
        except UserAccount.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    
    def get_user(self, user_id):
        """Get user by ID."""
        try:
            return UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist:
            return None
