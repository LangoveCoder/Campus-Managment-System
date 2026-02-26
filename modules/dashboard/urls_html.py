"""
Dashboard HTML URL routes.

Mounted at /dashboard/ in config/urls.py (no api/ prefix).
Kept separate from urls.py (JSON API routes) to avoid namespace collision.
"""
from django.urls import path
from . import views_html

urlpatterns = [
    path('', views_html.dashboard_home, name='dashboard_home'),
]
