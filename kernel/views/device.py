"""
Device Views/API

Endpoints for device management and communication.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from kernel.models import Device
import json

@csrf_exempt
@require_POST
def device_heartbeat_view(request):
    """
    API for devices to report status.
    Expected JSON: {
        "driver_identifier": "HW-ID-123",
        "status": "ONLINE",
        "ip_address": "192.168.1.50" (optional)
    }
    """
    try:
        data = json.loads(request.body)
        driver_identifier = data.get('driver_identifier')
        status = data.get('status', 'ONLINE')
        ip_address = data.get('ip_address')

        if not driver_identifier:
            return JsonResponse({'error': 'Missing driver_identifier'}, status=400)

        try:
            device = Device.objects.get(driver_identifier=driver_identifier)
            device.status = status
            device.last_heartbeat = timezone.now()
            if ip_address:
                device.ip_address = ip_address
            device.save()
            
            return JsonResponse({'status': 'success', 'device_name': device.name})
            
        except Device.DoesNotExist:
            return JsonResponse({'error': 'Device not registered'}, status=404)

    except Exception as e:
        return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)
