"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # Authentication URLs
    path("dashboard/", include("modules.dashboard.urls_html")),
    path("academics/", include("modules.academics.urls_html")),
    path("attendance/", include("modules.attendance.urls_html")),
    path("admissions/", include("modules.admissions.urls_html")),
    path("workforce/", include("modules.workforce.urls_html")),
    path("profiles/", include("modules.profiles.urls_html", namespace="profiles")),
    path("timetable/", include("modules.timetable.urls_html")),
    path("media-assets/", include("modules.media.urls_html")),
    path("superadmin/", include("modules.superadmin.urls_html")),
    path("", include("kernel.urls")),                        # Kernel UI + API
    path("api/dashboard/", include("modules.dashboard.urls")),
    path("api/academics/", include("modules.academics.urls")),
    path("api/admissions/", include("modules.admissions.urls")),
    path("api/attendance/", include("modules.attendance.urls")),
    path("api/workforce/", include("modules.workforce.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
