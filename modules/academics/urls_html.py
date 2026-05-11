from django.urls import path
from . import views_html

urlpatterns = [
    path('', views_html.program_list, name='program_list'),
    path('programs/create/', views_html.create_program, name='create_program'),
    path('programs/<int:program_id>/', views_html.program_detail, name='program_detail'),
    path('programs/<int:program_id>/cycles/create/', views_html.create_cycle, name='create_cycle'),
    path('programs/<int:program_id>/cycles/<int:cycle_id>/classes/create/', views_html.create_class_group, name='create_class_group'),
    path('classes/<int:class_group_id>/', views_html.class_detail, name='class_detail'),
    path('classes/<int:class_group_id>/results/', views_html.class_results, name='class_results'),
    path('enroll/', views_html.enroll_student, name='enroll_student'),
]
