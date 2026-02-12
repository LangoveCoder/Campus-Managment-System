"""
Test Script for Phase 2 Services

This script tests all Phase 2 services and seeds permissions.
Run with: python test_phase2.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from kernel.models import Permission, Role, RolePermissionMap, Campus, Person
from kernel.services import IdentityService, AuthorizationService, RoleBindingService, PersonService
from datetime import datetime, timedelta
from django.utils import timezone

print("=" * 60)
print("PHASE 2 SERVICES TEST")
print("=" * 60)

# Step 1: Seed Permissions
print("\n1. Seeding Permissions...")
permissions_data = [
    ('kernel.view_person', 'View Person', 'Can view person details', False),
    ('kernel.add_person', 'Add Person', 'Can create new persons', False),
    ('kernel.change_person', 'Change Person', 'Can update person details', False),
    ('kernel.delete_person', 'Delete Person', 'Can deactivate persons', True),
    ('kernel.view_useraccount', 'View User Account', 'Can view user accounts', False),
    ('kernel.add_useraccount', 'Add User Account', 'Can create user accounts', False),
    ('kernel.change_useraccount', 'Change User Account', 'Can update user accounts', False),
    ('kernel.lock_useraccount', 'Lock User Account', 'Can lock/unlock user accounts', True),
    ('kernel.view_campus', 'View Campus', 'Can view campus details', False),
    ('kernel.add_campus', 'Add Campus', 'Can create campuses', True),
    ('kernel.change_campus', 'Change Campus', 'Can update campus details', False),
    ('kernel.view_role', 'View Role', 'Can view roles', False),
    ('kernel.assign_role', 'Assign Role', 'Can assign roles to users', True),
    ('kernel.revoke_role', 'Revoke Role', 'Can revoke role assignments', True),
    ('kernel.view_permissions', 'View Permissions', 'Can view all permissions', False),
    ('kernel.manage_permissions', 'Manage Permissions', 'Can manage role-permission mappings', True),
]

created_perms = 0
for code, name, desc, is_dangerous in permissions_data:
    perm, created = Permission.objects.update_or_create(
        code=code,
        defaults={'name': name, 'module': 'kernel', 'description': desc, 'is_dangerous': is_dangerous}
    )
    if created:
        created_perms += 1
        print(f"  ✓ Created: {code}")
    else:
        print(f"  - Updated: {code}")

print(f"\n  Total: {created_perms} created, {len(permissions_data) - created_perms} updated")

# Step 2: Seed Role-Permission Mappings
print("\n2. Seeding Role-Permission Mappings...")
all_perm_codes = set([p[0] for p in permissions_data])

role_mappings = {
    'SUPER_ADMIN': all_perm_codes,
    'CAMPUS_ADMIN': {
        'kernel.view_person', 'kernel.add_person', 'kernel.change_person',
        'kernel.view_useraccount', 'kernel.add_useraccount', 'kernel.change_useraccount',
        'kernel.lock_useraccount', 'kernel.view_campus', 'kernel.change_campus',
        'kernel.view_role', 'kernel.assign_role', 'kernel.revoke_role', 'kernel.view_permissions'
    },
    'REGISTRAR': {
        'kernel.view_person', 'kernel.add_person', 'kernel.change_person',
        'kernel.view_useraccount', 'kernel.add_useraccount', 'kernel.change_useraccount',
        'kernel.view_campus', 'kernel.view_role'
    },
    'FACULTY': {'kernel.view_person', 'kernel.view_useraccount', 'kernel.view_campus', 'kernel.view_role'},
    'STUDENT': {'kernel.view_person', 'kernel.view_campus'},
}

created_mappings = 0
for role_name, perm_codes in role_mappings.items():
    role = Role.objects.get(name=role_name)
    for perm_code in perm_codes:
        perm = Permission.objects.get(code=perm_code)
        mapping, created = RolePermissionMap.objects.get_or_create(
            role=role, permission=perm, defaults={'granted_by': None}
        )
        if created:
            created_mappings += 1

print(f"  ✓ Created {created_mappings} role-permission mappings")

# Step 3: Test IdentityService
print("\n3. Testing IdentityService...")
try:
    test_person = IdentityService.create_person(
        full_name="Test Teacher",
        primary_phone="+92-300-1234567",
        primary_email="test.teacher@campus.edu"
    )
    print(f"  ✓ Created person: {test_person.full_name} (ID: {test_person.id})")
    
    # Test retrieval
    retrieved = IdentityService.get_person_by_email("test.teacher@campus.edu")
    print(f"  ✓ Retrieved person by email: {retrieved.full_name}")
    
    # Test update
    updated = IdentityService.update_person(test_person.id, full_name="Updated Teacher Name")
    print(f"  ✓ Updated person: {updated.full_name}")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

# Step 4: Test RoleBindingService
print("\n4. Testing RoleBindingService...")
try:
    # Create test campus if needed
    campus, _ = Campus.objects.get_or_create(
        name="Test Campus",
        defaults={'campus_type': 'PHYSICAL', 'is_active': True}
    )
    
    # Get FACULTY role
    faculty_role = Role.objects.get(name='FACULTY')
    
    # Create binding
    binding = RoleBindingService.create_binding(
        person_id=test_person.id,
        role_id=faculty_role.id,
        campus_id=campus.id,
        valid_from=timezone.now(),
        valid_until=timezone.now() + timedelta(days=365)
    )
    print(f"  ✓ Created role binding: {test_person.full_name} as {faculty_role.name} at {campus.name}")
    
    # Test binding queries
    bindings = RoleBindingService.get_bindings_for_person(test_person.id)
    print(f"  ✓ Found {bindings.count()} active binding(s) for person")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

# Step 5: Test AuthorizationService
print("\n5. Testing AuthorizationService...")
try:
    # Get all permissions for the person
    all_perms = AuthorizationService.get_all_permissions(test_person.id, campus.id)
    print(f"  ✓ Person has {len(all_perms)} permissions")
    print(f"    Permissions: {', '.join(sorted(list(all_perms)[:5]))}...")
    
    # Test specific permission
    has_view = AuthorizationService.has_permission(
        test_person.id, campus.id, 'kernel.view_person'
    )
    print(f"  ✓ Has 'kernel.view_person': {has_view}")
    
    has_delete = AuthorizationService.has_permission(
        test_person.id, campus.id, 'kernel.delete_person'
    )
    print(f"  ✓ Has 'kernel.delete_person': {has_delete}")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

# Step 6: Test PersonService
print("\n6. Testing PersonService...")
try:
    # Get person summary
    summary = PersonService.get_person_summary(test_person.id)
    print(f"  ✓ Person Summary:")
    print(f"    Name: {summary['person'].full_name}")
    print(f"    Roles: {[r.name for r in summary['roles']]}")
    print(f"    Campuses: {[c.name for c in summary['campuses']]}")
    print(f"    Total Bindings: {summary['total_bindings']}")
    
    # Test search
    results = PersonService.search_persons("Test")
    print(f"  ✓ Search for 'Test' found {results.count()} person(s)")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("PHASE 2 SERVICES TEST COMPLETE!")
print("=" * 60)
print(f"\nDatabase Summary:")
print(f"  - Permissions: {Permission.objects.count()}")
print(f"  - Role-Permission Mappings: {RolePermissionMap.objects.count()}")
print(f"  - Persons: {Person.objects.count()}")
print(f"  - Campuses: {Campus.objects.count()}")
print("=" * 60)
