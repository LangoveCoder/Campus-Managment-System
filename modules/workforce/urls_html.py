from django.urls import path
from . import views_html

urlpatterns = [
    path('', views_html.workforce_dashboard, name='workforce_dashboard'),
    path('attendance/', views_html.workforce_attendance, name='workforce_attendance'),
    path('log/', views_html.workforce_log, name='workforce_log'),
    path('devices/', views_html.workforce_devices, name='workforce_devices'),
    path('staff/', views_html.staff_list, name='staff_list'),
    path('staff/add/', views_html.add_staff, name='add_staff'),
]
