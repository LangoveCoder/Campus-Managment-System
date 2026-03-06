from django.urls import path
from modules.timetable import views_html

urlpatterns = [
    path('', views_html.timetable_view, name='timetable'),
    path('add/', views_html.add_slot, name='timetable_add_slot'),
    path('rooms/', views_html.rooms_view, name='timetable_rooms'),
    path('rooms/add/', views_html.add_room, name='timetable_add_room'),
    path('rooms/delete/<int:room_id>/', views_html.delete_room, name='timetable_delete_room'),
]
