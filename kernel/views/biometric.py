"""
Biometric Views/API

Endpoints for biometric enrollment and authentication.
"""
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from kernel.services import BiometricService, PersonService, IdentityService
import json
import base64

@csrf_exempt  # For now, until we handle CSRF in the hardware bridge/client
@require_POST
def enroll_biometric_view(request):
    """
    API to enroll biometric data.
    Expected JSON: {
        "person_id": "UUID",
        "biometric_type": "FINGERPRINT",
        "data_base64": "...",
        "device_id": "UUID" (optional)
    }
    """
    try:
        data = json.loads(request.body)
        person_id = data.get('person_id')
        biometric_type = data.get('biometric_type')
        data_base64 = data.get('data_base64')
        device_id = data.get('device_id')

        if not all([person_id, biometric_type, data_base64]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Decode base64 data
        try:
            biometric_bytes = base64.b64decode(data_base64)
        except Exception:
            return JsonResponse({'error': 'Invalid base64 data'}, status=400)

        biometric = BiometricService.enroll_biometric(
            person_id=person_id,
            biometric_type=biometric_type,
            biometric_data=biometric_bytes,
            device_id=device_id
        )

        return JsonResponse({
            'status': 'success',
            'biometric_id': str(biometric.id),
            'quality_score': biometric.quality_score
        })

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)


@csrf_exempt
@require_POST
def authenticate_biometric_view(request):
    """
    API to authenticate via biometric.
    Expected JSON: {
        "biometric_type": "FINGERPRINT",
        "data_base64": "..."
    }
    """
    try:
        data = json.loads(request.body)
        biometric_type = data.get('biometric_type')
        data_base64 = data.get('data_base64')

        if not all([biometric_type, data_base64]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Decode base64 data
        try:
            biometric_bytes = base64.b64decode(data_base64)
        except Exception:
            return JsonResponse({'error': 'Invalid base64 data'}, status=400)

        person = BiometricService.authenticate_biometric(
            biometric_type=biometric_type,
            biometric_data=biometric_bytes
        )

        if person:
            # Check if there is a UserAccount for this person and log them in?
            # For now, just return the person details and success.
            # In a real app, we might create a session here if the user account exists.
            
            # TODO: Link to UserAccount login if applicable
            
            return JsonResponse({
                'status': 'success',
                'person_id': str(person.id),
                'full_name': person.full_name
            })
        else:
            return JsonResponse({'status': 'failure', 'error': 'No match found'}, status=401)

    except Exception as e:
        return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)


from django.shortcuts import render, get_object_or_404
from kernel.models import Person

def enrollment_page(request, person_id):
    """
    Renders the biometric enrollment page for a specific person.
    """
    person = get_object_or_404(Person, id=person_id)
    return render(request, 'kernel/biometric/enrollment.html', {'person': person})
