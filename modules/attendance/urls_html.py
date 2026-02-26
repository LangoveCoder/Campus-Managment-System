from django.urls import path
from . import views_html

urlpatterns = [
    path('', views_html.attendance_home, name='attendance_home'),
    path('sessions/mark/<int:class_group_id>/', views_html.mark_attendance, name='mark_attendance'),
    path('summary/<int:class_group_id>/', views_html.attendance_summary, name='attendance_summary'),
    path('sessions/list/<int:class_group_id>/', views_html.session_list, name='session_list'),
    path('student/<int:enrollment_id>/', views_html.student_history, name='student_history'),
]
