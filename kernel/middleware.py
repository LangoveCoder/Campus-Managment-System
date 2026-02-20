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


class JWTAuthenticationMiddleware:
    """
    Kernel JWT Authentication Middleware.

    Reads the Authorization: Bearer <token> header, decodes and validates
    the JWT, resolves the Person from its person_id claim, and injects
    request.person and request.person_id into the request object.

    Design: PASSIVE. Never raises. Never redirects. Sets to None on any
    failure and moves on — views are responsible for enforcement.

    Token spec:
        Algorithm : HS256
        Secret    : settings.SECRET_KEY
        Claims    : person_id (str UUID), campus_id, iat, exp
        Expiry    : 24 hours
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.person = None
        request.person_id = None

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[len('Bearer '):]
            self._resolve_person(request, token)

        return self.get_response(request)

    def _resolve_person(self, request, token: str) -> None:
        """Decode token and hydrate request.person / request.person_id. Silent on failure."""
        import jwt
        from django.conf import settings
        from kernel.models import Person

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256'],
            )
            person_id = payload.get('person_id')
            if not person_id:
                return

            person = Person.objects.get(id=person_id)
            request.person = person
            request.person_id = person_id

        except jwt.ExpiredSignatureError:
            pass  # token expired — request.person stays None
        except jwt.InvalidTokenError:
            pass  # bad signature, malformed, etc.
        except Person.DoesNotExist:
            pass  # person deleted since token was issued
        except Exception:
            pass  # catch-all — middleware must never crash a request

