"""
Attendance Module URL Configuration
Prefix: api/attendance/ (wired in config/urls.py)
"""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Session management
    path('sessions/create/',
         views.CreateSessionView.as_view(),
         name='session_create'),

    # Single-record marking (delegates to mark_bulk with 1 record)
    path('sessions/<int:session_id>/mark/',
         views.MarkSingleView.as_view(),
         name='session_mark'),

    # Bulk marking
    path('sessions/<int:session_id>/mark-bulk/',
         views.MarkBulkView.as_view(),
         name='session_mark_bulk'),

    # Session report (all records for a session)
    path('sessions/<int:session_id>/report/',
         views.SessionReportView.as_view(),
         name='session_report'),

    # Attendance summary by class + date range
    path('summary/',
         views.AttendanceSummaryView.as_view(),
         name='summary'),
]
