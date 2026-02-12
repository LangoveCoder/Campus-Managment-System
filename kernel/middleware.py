"""
Campus Context Middleware

Sets campus context for each request based on session data.
"""
from django.shortcuts import redirect
from django.urls import reverse
from .context import set_current_campus_id, clear_campus_context, set_current_person_id


class CampusContextMiddleware:
    """
    Middleware to set campus context for each request.
    
    Flow:
    1. Check if request should be skipped (admin, static, login, etc.)
    2. Get campus_id from session
    3. If no campus and user is authenticated, redirect to campus picker
    4. Set thread-local context (campus_id and person_id)
    5. Process request
    6. Clear context after request (prevent leakage)
    
    Usage:
        Add to MIDDLEWARE in settings.py:
        MIDDLEWARE = [
            ...
            'kernel.middleware.CampusContextMiddleware',
        ]
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip for certain URLs
        if self._should_skip(request):
            return self.get_response(request)
        
        # Get campus_id from session
        campus_id = request.session.get('current_campus_id')
        
        # If no campus selected and user is authenticated, redirect to picker
        if campus_id is None and request.user.is_authenticated:
            # Check if user has a person record
            if hasattr(request.user, 'person') and request.user.person:
                # Don't redirect if already on select_campus page
                if request.path != reverse('kernel:select_campus'):
                    return redirect('kernel:select_campus')
        
        # Set thread-local context
        if campus_id is not None:
            set_current_campus_id(campus_id)
        
        # Set person_id if user is authenticated
        if request.user.is_authenticated:
            if hasattr(request.user, 'person') and request.user.person:
                set_current_person_id(request.user.person.id)
        
        # Attach campus_id to request for easy access in views
        request.campus_id = campus_id
        
        # Process request
        response = self.get_response(request)
        
        # Clear context after request to prevent leakage
        clear_campus_context()
        
        return response
    
    def _should_skip(self, request):
        """
        Check if middleware should skip this request.
        
        Skip for:
        - Admin interface
        - Static files
        - Media files
        - Login/logout pages
        - Campus selection page
        
        Args:
            request: Django request object
            
        Returns:
            True if should skip, False otherwise
        """
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/accounts/login/',
            '/accounts/logout/',
        ]
        
        # Check if path starts with any skip path
        for path in skip_paths:
            if request.path.startswith(path):
                return True
        
        return False
