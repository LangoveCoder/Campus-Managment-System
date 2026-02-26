"""
Management Command: Seed Role-Permission Mappings

Creates default role-permission mappings for all system roles.
"""
from django.core.management.base import BaseCommand
from kernel.models import Role, Permission, RolePermissionMap


class Command(BaseCommand):
    help = 'Seed default role-permission mappings'

    def handle(self, *args, **options):
        """Create default role-permission mappings."""
        
        # Get all permissions across all modules
        all_perms = set(Permission.objects.values_list('code', flat=True))
        
        # Define role-permission mappings
        role_permissions = {
            'SUPER_ADMIN': all_perms,  # Super admin gets everything
            
            'CAMPUS_ADMIN': {
                'kernel.view_person',
                'kernel.add_person',
                'kernel.change_person',
                'kernel.view_useraccount',
                'kernel.add_useraccount',
                'kernel.change_useraccount',
                'kernel.lock_useraccount',
                'kernel.view_campus',
                'kernel.change_campus',
                'kernel.view_role',
                'kernel.assign_role',
                'kernel.revoke_role',
                'kernel.view_permissions',
                'academics.view_program',
                'academics.view_class',
                'academics.enroll_student',
                'admissions.view_applicant',
                'admissions.create_applicant',
                'admissions.evaluate_test',
                'admissions.evaluate_interview',
                'admissions.decide_application',
                'admissions.convert_to_enrollment',
                'attendance.view_attendance',
                'attendance.mark_attendance',
                'workforce.view_attendance',
                'workforce.manage_devices',
            },
            
            'REGISTRAR': {
                'kernel.view_person',
                'kernel.add_person',
                'kernel.change_person',
                'kernel.view_useraccount',
                'kernel.add_useraccount',
                'kernel.change_useraccount',
                'kernel.view_campus',
                'kernel.view_role',
                'academics.view_program',
                'academics.view_class',
                'academics.enroll_student',
                'admissions.view_applicant',
                'admissions.create_applicant',
                'admissions.convert_to_enrollment',
            },
            
            'FACULTY': {
                'kernel.view_person',
                'kernel.view_useraccount',
                'kernel.view_campus',
                'kernel.view_role',
                'academics.view_program',
                'academics.view_class',
                'attendance.view_attendance',
                'attendance.mark_attendance',
            },
            
            'STUDENT': {
                'kernel.view_person',  # Can view own person record
                'kernel.view_campus',
                'academics.view_program', # View own program
                'attendance.view_attendance', # View own attendance
            },
            
            'PARENT': {
                'kernel.view_person',  # Can view child's person record
                'kernel.view_campus',
                'academics.view_program',
                'attendance.view_attendance',
            },
            
            'ACCOUNTANT': {
                'kernel.view_person',
                'kernel.view_useraccount',
                'kernel.view_campus',
            },
            
            'LIBRARIAN': {
                'kernel.view_person',
                'kernel.view_useraccount',
                'kernel.view_campus',
            },
            
            'SECURITY': {
                'kernel.view_person',
                'kernel.view_campus',
                'attendance.view_attendance', # View gate logs
            },
        }
        
        created_count = 0
        skipped_count = 0
        
        for role_name, permission_codes in role_permissions.items():
            try:
                role = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Role {role_name} not found, skipping...')
                )
                continue
            
            for perm_code in permission_codes:
                try:
                    permission = Permission.objects.get(code=perm_code)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Permission {perm_code} not found, skipping...')
                    )
                    continue
                
                # Create mapping if it doesn't exist
                mapping, created = RolePermissionMap.objects.get_or_create(
                    role=role,
                    permission=permission,
                    defaults={'granted_by': None}  # System-granted
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Granted {permission.code} to {role.name}'
                        )
                    )
                else:
                    skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {created_count} mappings created, {skipped_count} already existed'
            )
        )
