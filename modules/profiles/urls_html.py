from django.urls import path
from . import views_html

app_name = 'profiles'

urlpatterns = [
    path('<uuid:person_id>/edit/', views_html.edit_profile, name='edit_profile'),
]
