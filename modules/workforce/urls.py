"""
Workforce Module URL Configuration
Prefix: api/workforce/ (wired in config/urls.py)
"""
from django.urls import path
from . import views

app_name = 'workforce'

urlpatterns = [
    # Device management
    path('devices/enroll/',
         views.DeviceEnrollView.as_view(),
         name='device_enroll'),               # LIVE

    path('devices/',
         views.DeviceListView.as_view(),
         name='device_list'),                 # GAP-1

    # Punch log ingestion
    path('logs/punch/',
         views.PunchLogView.as_view(),
         name='punch_log'),                   # GAP-2

    # Log queries
    path('logs/',
         views.EventLogView.as_view(),
         name='event_log'),                   # GAP-3

    # Daily attendance summary
    path('attendance/summary/',
         views.AttendanceSummaryView.as_view(),
         name='attendance_summary'),          # GAP-4
]
