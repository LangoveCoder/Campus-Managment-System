
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from kernel.models import Permission

def seed_permissions():
    """Seeds the database with granular permissions."""
    print("Seeding Permissions...")
    
    perms = [
        # Person
        ('person.create', 'Can create person'),
        ('person.view', 'Can view person details'),
        ('person.edit', 'Can edit person details'),
        ('person.delete', 'Can delete person'),
        
        # Biometrics
        ('biometric.enroll', 'Can enroll biometric data'),
        ('biometric.verify', 'Can verify biometric data'),
        ('biometric.delete', 'Can delete biometric data'),
        
        # User Account
        ('user.create', 'Can create user account'),
        ('user.manage', 'Can manage user account'),
        
        # Role Binding
        ('binding.create', 'Can assign roles'),
        ('binding.view', 'Can view role assignments'),
        ('binding.delete', 'Can revoke roles'),
        
        # Audit
        ('audit.view', 'Can view audit logs'),
    ]
    
    count = 0
    for codename, desc in perms:
        obj, created = Permission.objects.get_or_create(
            codename=codename,
            defaults={'description': desc}
        )
        if created:
            count += 1
            print(f"  [+] Created: {codename}")
        else:
            print(f"  [.] Exists: {codename}")
            
    print(f"Done. Created {count} permissions.")

if __name__ == "__main__":
    seed_permissions()
