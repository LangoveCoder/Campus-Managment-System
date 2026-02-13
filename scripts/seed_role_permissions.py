
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from kernel.models import Role, Permission

def seed_role_permissions():
    """Binds default permissions to roles."""
    print("Seeding Role Permissions...")
    
    # Define Roles and their Permissions
    role_map = {
        'admin': [
            'person.create', 'person.view', 'person.edit', 'person.delete',
            'biometric.enroll', 'biometric.verify', 'biometric.delete',
            'user.create', 'user.manage',
            'binding.create', 'binding.view', 'binding.delete',
            'audit.view'
        ],
        'registrar': [
            'person.create', 'person.view', 'person.edit',
            'biometric.enroll', 'biometric.verify',
            'binding.view'
        ],
        'security': [
            'person.view',
            'biometric.verify'
        ],
        'student': [
            # Students mostly consume, permission layout might differ for self-service
            # Typically no specific permissions on others
            'person.view' # view self
        ],
        'teacher': [
            'person.view'
        ]
    }
    
    for role_name, perms in role_map.items():
        role, _ = Role.objects.get_or_create(name=role_name)
        print(f"Configuring Role: {role_name}")
        
        for perm_code in perms:
            try:
                p = Permission.objects.get(codename=perm_code)
                role.permissions.add(p)
                print(f"  -> Added {perm_code}")
            except Permission.DoesNotExist:
                print(f"  [!] Warning: Permission {perm_code} not found. Run seed_permissions.py first.")
                
    print("Done.")

if __name__ == "__main__":
    seed_role_permissions()
