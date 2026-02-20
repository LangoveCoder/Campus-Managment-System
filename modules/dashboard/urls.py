from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('home/', views.DashboardHomeView.as_view(), name='home'),
    path('attendance/', views.AttendanceSummaryView.as_view(), name='attendance'),
    path('assessments/', views.AssessmentSummaryView.as_view(), name='assessments'),
]
