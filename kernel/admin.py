"""
Django Admin Configuration for Kernel Models
"""
from django.contrib import admin
from .models import (
    Person,
    Campus,
    Role,
    Permission,
    UserAccount,
    RolePermissionMap,
    UserRoleBinding,
    BiometricIdentity,
)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'primary_email', 'primary_phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'primary_email', 'primary_phone']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ['name', 'campus_type', 'is_active', 'created_at']
    list_filter = ['campus_type', 'is_active']
    search_fields = ['name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_system_role', 'created_at']
    list_filter = ['is_system_role']
    search_fields = ['name', 'description']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'module', 'is_dangerous', 'created_at']
    list_filter = ['module', 'is_dangerous']
    search_fields = ['code', 'name', 'module']


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'person', 'email', 'is_locked', 'last_login']
    list_filter = ['is_locked', 'created_at']
    search_fields = ['username', 'email', 'person__full_name']
    readonly_fields = ['id', 'created_at', 'last_login']


@admin.register(RolePermissionMap)
class RolePermissionMapAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'granted_by', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['role__name', 'permission__code']
    readonly_fields = ['created_at']


@admin.register(UserRoleBinding)
class UserRoleBindingAdmin(admin.ModelAdmin):
    list_display = ['person', 'role', 'campus', 'valid_from', 'valid_until', 'is_active']
    list_filter = ['role', 'campus', 'is_active', 'valid_from']
    search_fields = ['person__full_name', 'role__name', 'campus__name']
    readonly_fields = ['id', 'created_at', 'deactivated_at']


@admin.register(BiometricIdentity)
class BiometricIdentityAdmin(admin.ModelAdmin):
    list_display = ['person', 'biometric_type', 'quality_score', 'is_active', 'created_at']
    list_filter = ['biometric_type', 'is_active', 'created_at']
    search_fields = ['person__full_name', 'enrollment_device_id']
    readonly_fields = ['id', 'created_at', 'deactivated_at']
