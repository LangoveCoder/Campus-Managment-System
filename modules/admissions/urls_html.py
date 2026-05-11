from django.urls import path
from . import views_html

urlpatterns = [
    path('apply/', views_html.apply, name='apply'),
    path('', views_html.applications_list, name='applications_list'),
    path('applications/<int:app_id>/', views_html.application_detail, name='application_detail'),
    path('applications/<int:app_id>/test-result/', views_html.test_result, name='test_result'),
    path('applications/<int:app_id>/decision/', views_html.make_decision, name='make_decision'),
    path('applications/<int:app_id>/interview/', views_html.record_interview, name='record_interview'),
    path('import-merit-list/', views_html.import_merit_list, name='import_merit_list'),
    path('config/', views_html.admission_config, name='admission_config'),
    path('merit-list/', views_html.merit_list_view, name='merit_list'),
]
