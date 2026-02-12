"""
Kernel URL Configuration

URL patterns for kernel app.
"""
from django.urls import path
from .views import context, audit

app_name = 'kernel'

urlpatterns = [
    path('select-campus/', context.select_campus, name='select_campus'),
    path('switch-campus/', context.switch_campus, name='switch_campus'),
    path('dashboard/', context.dashboard, name='dashboard'),
    path('audit/', audit.audit_log_list, name='audit_list'),
    path('', context.dashboard, name='home'),  # Default to dashboard
]
