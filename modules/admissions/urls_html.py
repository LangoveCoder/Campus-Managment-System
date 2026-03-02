from django.urls import path
from . import views_html

urlpatterns = [
    path('apply/', views_html.apply, name='apply'),
    path('', views_html.applications_list, name='applications_list'),
    path('applications/<int:app_id>/', views_html.application_detail, name='application_detail'),
    path('applications/<int:app_id>/test-result/', views_html.test_result, name='test_result'),
    path('applications/<int:app_id>/decision/', views_html.make_decision, name='make_decision'),
]
