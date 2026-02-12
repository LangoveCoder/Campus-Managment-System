"""
Management Command: Seed Kernel Permissions

Creates all kernel module permissions in the database.
"""
from django.core.management.base import BaseCommand
from kernel.models import Permission


class Command(BaseCommand):
    help = 'Seed kernel module permissions'

    def handle(self, *args, **options):
        """Create all kernel permissions."""
        
        permissions = [
            # Person permissions
            {
                'code': 'kernel.view_person',
                'name': 'View Person',
                'module': 'kernel',
                'description': 'Can view person details',
                'is_dangerous': False
            },
            {
                'code': 'kernel.add_person',
                'name': 'Add Person',
                'module': 'kernel',
                'description': 'Can create new persons',
                'is_dangerous': False
            },
            {
                'code': 'kernel.change_person',
                'name': 'Change Person',
                'module': 'kernel',
                'description': 'Can update person details',
                'is_dangerous': False
            },
            {
                'code': 'kernel.delete_person',
                'name': 'Delete Person',
                'module': 'kernel',
                'description': 'Can deactivate persons',
                'is_dangerous': True
            },
            
            # UserAccount permissions
            {
                'code': 'kernel.view_useraccount',
                'name': 'View User Account',
                'module': 'kernel',
                'description': 'Can view user accounts',
                'is_dangerous': False
            },
            {
                'code': 'kernel.add_useraccount',
                'name': 'Add User Account',
                'module': 'kernel',
                'description': 'Can create user accounts',
                'is_dangerous': False
            },
            {
                'code': 'kernel.change_useraccount',
                'name': 'Change User Account',
                'module': 'kernel',
                'description': 'Can update user accounts',
                'is_dangerous': False
            },
            {
                'code': 'kernel.lock_useraccount',
                'name': 'Lock User Account',
                'module': 'kernel',
                'description': 'Can lock/unlock user accounts',
                'is_dangerous': True
            },
            
            # Campus permissions
            {
                'code': 'kernel.view_campus',
                'name': 'View Campus',
                'module': 'kernel',
                'description': 'Can view campus details',
                'is_dangerous': False
            },
            {
                'code': 'kernel.add_campus',
                'name': 'Add Campus',
                'module': 'kernel',
                'description': 'Can create campuses',
                'is_dangerous': True
            },
            {
                'code': 'kernel.change_campus',
                'name': 'Change Campus',
                'module': 'kernel',
                'description': 'Can update campus details',
                'is_dangerous': False
            },
            
            # Role permissions
            {
                'code': 'kernel.view_role',
                'name': 'View Role',
                'module': 'kernel',
                'description': 'Can view roles',
                'is_dangerous': False
            },
            {
                'code': 'kernel.assign_role',
                'name': 'Assign Role',
                'module': 'kernel',
                'description': 'Can assign roles to users',
                'is_dangerous': True
            },
            {
                'code': 'kernel.revoke_role',
                'name': 'Revoke Role',
                'module': 'kernel',
                'description': 'Can revoke role assignments',
                'is_dangerous': True
            },
            
            # Permission management
            {
                'code': 'kernel.view_permissions',
                'name': 'View Permissions',
                'module': 'kernel',
                'description': 'Can view all permissions',
                'is_dangerous': False
            },
            {
                'code': 'kernel.manage_permissions',
                'name': 'Manage Permissions',
                'module': 'kernel',
                'description': 'Can manage role-permission mappings',
                'is_dangerous': True
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for perm_data in permissions:
            permission, created = Permission.objects.update_or_create(
                code=perm_data['code'],
                defaults={
                    'name': perm_data['name'],
                    'module': perm_data['module'],
                    'description': perm_data['description'],
                    'is_dangerous': perm_data['is_dangerous']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created permission: {permission.code}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated permission: {permission.code}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {created_count} created, {updated_count} updated'
            )
        )
