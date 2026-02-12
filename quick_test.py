"""Quick test of Phase 2 services"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from kernel.models import Permission, Role, Campus
from kernel.services import IdentityService, AuthorizationService

# Check if permissions exist
perm_count = Permission.objects.count()
print(f"✓ Permissions in database: {perm_count}")

# Check if roles exist
role_count = Role.objects.count()
print(f"✓ Roles in database: {role_count}")

# Check if campuses exist
campus_count = Campus.objects.count()
print(f"✓ Campuses in database: {campus_count}")

# Test IdentityService
from kernel.models import Person
person_count = Person.objects.count()
print(f"✓ Persons in database: {person_count}")

print("\n✅ All services are importable and database is accessible!")
