"""
RolePermissionMap Model - Role-Permission Association

Maps permissions to roles.
"""
from django.db import models
from .role import Role
from .permission import Permission
from .user_account import UserAccount


class RolePermissionMap(models.Model):
    """
    Maps permissions to roles.
    
    Defines what a role can do.
    
    Constitution Reference: Section 2.6
    """
    
    id = models.BigAutoField(primary_key=True)
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permission_maps',
        help_text="The role"
    )
    
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_maps',
        help_text="The permission"
    )
    
    granted_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Who granted this permission"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'kernel_role_permission_map'
        verbose_name = 'Role Permission Map'
        verbose_name_plural = 'Role Permission Maps'
        unique_together = [['role', 'permission']]
    
    def __str__(self) -> str:
        return f"{self.role.name} → {self.permission.code}"
    
    def __repr__(self) -> str:
        return f"<RolePermissionMap: {self.role.name} → {self.permission.code}>"
