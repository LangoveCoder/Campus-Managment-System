"""
Auth Views — kernel/views/auth_views.py

JWT login endpoint.
URL: POST api/auth/login/
"""
import json
from datetime import datetime, timedelta, timezone as dt_timezone

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def login_view(request):
    """
    POST api/auth/login/

    Body: { "username": str, "password": str }

    Success (200):
        {
            "access_token": str,
            "person_id":    str (UUID),
            "name":         str
        }

    Failure (401):
        { "error": "Invalid credentials" }
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    username = body.get('username', '').strip()
    password = body.get('password', '').strip()

    if not username or not password:
        return JsonResponse({'error': 'username and password are required.'}, status=400)

    # Validate credentials against UserAccount (inherits AbstractUser)
    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({'error': 'Invalid credentials.'}, status=401)

    # Resolve linked Person
    person = getattr(user, 'person', None)
    if person is None:
        return JsonResponse(
            {'error': 'Account has no linked Person record. Contact administrator.'},
            status=403,
        )

    # Build JWT
    now = datetime.now(tz=dt_timezone.utc)
    payload = {
        'person_id': str(person.id),   # UUID → string for JSON serialisation
        'campus_id': None,             # Campus is selected separately after login
        'iat': now,
        'exp': now + timedelta(hours=24),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return JsonResponse({
        'access_token': token,
        'person_id': str(person.id),
        'name': person.full_name,
    })
