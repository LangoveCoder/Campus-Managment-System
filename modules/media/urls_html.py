from django.urls import path
from modules.media import views_html

urlpatterns = [
    path('upload/', views_html.upload_view, name='media_upload'),
    path('applicant-upload/', views_html.applicant_upload_view, name='media_applicant_upload'),
]
