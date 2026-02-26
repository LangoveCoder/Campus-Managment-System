"""
Admissions Module URL Configuration
Prefix: api/admissions/ (wired in config/urls.py)
"""
from django.urls import path
from . import views

app_name = 'admissions'

urlpatterns = [
    # Public submission — no JWT required
    path('apply/',
         views.ApplyView.as_view(),
         name='apply'),

    # Application queries — GAP (service methods missing)
    path('applications/',
         views.ApplicationListView.as_view(),
         name='application_list'),

    path('applications/<int:application_id>/',
         views.ApplicationDetailView.as_view(),
         name='application_detail'),

    # Application actions — LIVE (service handles auth internally)
    path('applications/<int:application_id>/test-result/',
         views.TestResultView.as_view(),
         name='test_result'),

    path('applications/<int:application_id>/interview/',
         views.InterviewView.as_view(),
         name='interview'),

    path('applications/<int:application_id>/decide/',
         views.DecideView.as_view(),
         name='decide'),

    path('applications/<int:application_id>/enroll/',
         views.EnrollView.as_view(),
         name='enroll'),
]
