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


@csrf_exempt
@require_POST
def set_campus_view(request):
    """
    POST api/auth/set-campus/

    Writes current_campus_id into the session so subsequent API calls
    have campus context (CampusContextMiddleware reads from session).

    Required for JWT/Flutter clients — browsers use the campus picker UI instead.

    Body: { "campus_id": int }

    Responses:
        200  { "status": "ok", "campus_id": int }
        400  Missing campus_id
        401  No valid JWT (request.person_id is None)
        403  Person has no active UserRoleBinding at that campus
        404  Campus does not exist
    """
    from django.utils import timezone
    from kernel.models import Campus, UserRoleBinding

    # 1. JWT auth check — person_id is set by JWTAuthenticationMiddleware
    person_id = getattr(request, 'person_id', None)
    if not person_id:
        return JsonResponse(
            {'error': 'Unauthorized', 'detail': 'Valid Bearer token required.'},
            status=401,
        )

    # 2. Parse body
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    campus_id = body.get('campus_id')
    if campus_id is None:
        return JsonResponse({'error': 'campus_id is required.'}, status=400)

    try:
        campus_id = int(campus_id)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'campus_id must be an integer.'}, status=400)

    # 3. Campus must exist
    try:
        campus = Campus.objects.get(id=campus_id)
    except Campus.DoesNotExist:
        return JsonResponse({'error': f'Campus {campus_id} not found.'}, status=404)

    # 4. Person must have at least one active binding at this campus
    #    Uses the same temporal validity pattern as UserRoleBinding everywhere else.
    has_binding = UserRoleBinding.objects.filter(
        person_id=person_id,
        campus_id=campus_id,
        is_active=True,
        validity__contains=timezone.now(),
    ).exists()

    if not has_binding:
        return JsonResponse(
            {
                'error': 'Forbidden',
                'detail': f'No active role at campus {campus.name}.',
            },
            status=403,
        )

    # 5. Write to session — CampusContextMiddleware reads this on every request
    request.session['current_campus_id'] = campus_id
    request.session.modified = True

    return JsonResponse({'status': 'ok', 'campus_id': campus_id})

