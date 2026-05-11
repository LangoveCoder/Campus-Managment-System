from django.urls import path
from modules.superadmin import views_html

urlpatterns = [
    path('campuses/', views_html.campuses_view, name='superadmin_campuses'),
    path('campuses/create/', views_html.create_campus_view, name='superadmin_create_campus'),
    path('campuses/delete/<int:campus_id>/', views_html.delete_campus_view, name='superadmin_delete_campus'),
]
