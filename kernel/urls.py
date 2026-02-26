"""
Kernel URL Configuration

URL patterns for kernel app.
"""
from django.urls import path
from django.views.generic import RedirectView
from .views import context, audit, biometric, device
from .views.auth_views import login_view, set_campus_view

app_name = 'kernel'

urlpatterns = [
    path('select-campus/', context.select_campus, name='select_campus'),
    path('switch-campus/', context.switch_campus, name='switch_campus'),
    path('audit/', audit.audit_log_list, name='audit_list'),
    
    # API endpoints
    path('api/auth/login/', login_view, name='api_login'),
    path('api/auth/set-campus/', set_campus_view, name='api_set_campus'),
    path('api/biometric/enroll', biometric.enroll_biometric_view, name='api_biometric_enroll'),
    path('api/biometric/auth', biometric.authenticate_biometric_view, name='api_biometric_auth'),
    path('api/device/heartbeat', device.device_heartbeat_view, name='api_device_heartbeat'),

    # UI Views
    path('enrollment/<uuid:person_id>/', biometric.enrollment_page, name='enrollment_page'),

    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='home'),
]
