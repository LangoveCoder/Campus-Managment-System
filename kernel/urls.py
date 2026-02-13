"""
Kernel URL Configuration

URL patterns for kernel app.
"""
from django.urls import path
from .views import context, audit, biometric, device

app_name = 'kernel'

urlpatterns = [
    path('select-campus/', context.select_campus, name='select_campus'),
    path('switch-campus/', context.switch_campus, name='switch_campus'),
    path('dashboard/', context.dashboard, name='dashboard'),
    path('audit/', audit.audit_log_list, name='audit_list'),
    
    # API endpoints
    path('api/biometric/enroll', biometric.enroll_biometric_view, name='api_biometric_enroll'),
    path('api/biometric/auth', biometric.authenticate_biometric_view, name='api_biometric_auth'),
    path('api/device/heartbeat', device.device_heartbeat_view, name='api_device_heartbeat'),

    # UI Views
    path('enrollment/<uuid:person_id>/', biometric.enrollment_page, name='enrollment_page'),

    path('', context.dashboard, name='home'),  # Default to dashboard
]
