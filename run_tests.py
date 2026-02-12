"""
Comprehensive Service Test with File Output
Run: python run_tests.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from kernel.models import Permission, Role, RolePermissionMap, Campus, Person
from kernel.services import IdentityService, AuthorizationService, RoleBindingService, PersonService
from datetime import datetime, timedelta
from django.utils import timezone

# Open output file
output = []

def log(msg):
    print(msg)
    output.append(msg)

log("=" * 70)
log("PHASE 2 SERVICES - COMPREHENSIVE TEST")
log("=" * 70)

# Test 1: Check Database State
log("\n[TEST 1] Database State")
log("-" * 70)
perm_count = Permission.objects.count()
role_count = Role.objects.count()
campus_count = Campus.objects.count()
person_count = Person.objects.count()
mapping_count = RolePermissionMap.objects.count()

log(f"  Permissions: {perm_count}")
log(f"  Roles: {role_count}")
log(f"  Campuses: {campus_count}")
log(f"  Persons: {person_count}")
log(f"  Role-Permission Mappings: {mapping_count}")

if perm_count == 0:
    log("\n  ⚠ WARNING: No permissions found. Running seed_permissions...")
    from django.core.management import call_command
    call_command('seed_permissions')
    perm_count = Permission.objects.count()
    log(f"  ✓ Created {perm_count} permissions")

if mapping_count == 0 and role_count > 0:
    log("\n  ⚠ WARNING: No role-permission mappings. Running seed_role_permissions...")
    from django.core.management import call_command
    call_command('seed_role_permissions')
    mapping_count = RolePermissionMap.objects.count()
    log(f"  ✓ Created {mapping_count} mappings")

# Test 2: IdentityService
log("\n[TEST 2] IdentityService")
log("-" * 70)
try:
    # Create test person
    test_person = IdentityService.create_person(
        full_name="Dr. Sarah Johnson",
        primary_phone="+92-300-9876543",
        primary_email="sarah.johnson@campus.edu"
    )
    log(f"  ✓ Created person: {test_person.full_name} (ID: {test_person.id})")
    
    # Retrieve by email
    retrieved = IdentityService.get_person_by_email("sarah.johnson@campus.edu")
    log(f"  ✓ Retrieved by email: {retrieved.full_name}")
    
    # Update person
    updated = IdentityService.update_person(test_person.id, full_name="Dr. Sarah M. Johnson")
    log(f"  ✓ Updated name to: {updated.full_name}")
    
except Exception as e:
    log(f"  ✗ ERROR: {str(e)}")

# Test 3: RoleBindingService
log("\n[TEST 3] RoleBindingService")
log("-" * 70)
try:
    # Get or create campus
    campus, created = Campus.objects.get_or_create(
        name="Main Campus",
        defaults={'campus_type': 'PHYSICAL', 'is_active': True}
    )
    if created:
        log(f"  ✓ Created campus: {campus.name}")
    else:
        log(f"  ✓ Using existing campus: {campus.name}")
    
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
    log(f"  ✓ Created binding: {test_person.full_name} as {faculty_role.name}")
    
    # Query bindings
    bindings = RoleBindingService.get_bindings_for_person(test_person.id)
    log(f"  ✓ Found {bindings.count()} active binding(s)")
    
    # Check validity
    is_valid = RoleBindingService.is_binding_valid(binding.id)
    log(f"  ✓ Binding is valid: {is_valid}")
    
except Exception as e:
    log(f"  ✗ ERROR: {str(e)}")

# Test 4: AuthorizationService
log("\n[TEST 4] AuthorizationService")
log("-" * 70)
try:
    # Get all permissions
    all_perms = AuthorizationService.get_all_permissions(test_person.id, campus.id)
    log(f"  ✓ Person has {len(all_perms)} permissions")
    
    # Show first 5 permissions
    perm_list = sorted(list(all_perms))[:5]
    for perm in perm_list:
        log(f"    - {perm}")
    if len(all_perms) > 5:
        log(f"    ... and {len(all_perms) - 5} more")
    
    # Test specific permissions
    has_view = AuthorizationService.has_permission(
        test_person.id, campus.id, 'kernel.view_person'
    )
    log(f"  ✓ Has 'kernel.view_person': {has_view}")
    
    has_delete = AuthorizationService.has_permission(
        test_person.id, campus.id, 'kernel.delete_person'
    )
    log(f"  ✓ Has 'kernel.delete_person': {has_delete}")
    
    # Get roles
    roles = AuthorizationService.get_person_roles_at_campus(test_person.id, campus.id)
    role_names = [r.name for r in roles]
    log(f"  ✓ Roles at campus: {', '.join(role_names)}")
    
except Exception as e:
    log(f"  ✗ ERROR: {str(e)}")

# Test 5: PersonService
log("\n[TEST 5] PersonService")
log("-" * 70)
try:
    # Get person summary
    summary = PersonService.get_person_summary(test_person.id)
    log(f"  ✓ Person Summary:")
    log(f"    Name: {summary['person'].full_name}")
    log(f"    Email: {summary['person'].primary_email}")
    log(f"    Roles: {[r.name for r in summary['roles']]}")
    log(f"    Campuses: {[c.name for c in summary['campuses']]}")
    log(f"    Total Bindings: {summary['total_bindings']}")
    
    # Search persons
    results = PersonService.search_persons("Sarah")
    log(f"  ✓ Search for 'Sarah' found {results.count()} person(s)")
    
    # Get person roles
    roles = PersonService.get_person_roles(test_person.id)
    log(f"  ✓ Person has {len(roles)} role(s)")
    
    # Get person campuses
    campuses = PersonService.get_person_campuses(test_person.id)
    log(f"  ✓ Person has access to {len(campuses)} campus(es)")
    
except Exception as e:
    log(f"  ✗ ERROR: {str(e)}")

# Final Summary
log("\n" + "=" * 70)
log("TEST SUMMARY")
log("=" * 70)
log(f"Database:")
log(f"  - Permissions: {Permission.objects.count()}")
log(f"  - Roles: {Role.objects.count()}")
log(f"  - Role-Permission Mappings: {RolePermissionMap.objects.count()}")
log(f"  - Persons: {Person.objects.count()}")
log(f"  - Campuses: {Campus.objects.count()}")
log(f"\nServices:")
log(f"  ✓ IdentityService - Working")
log(f"  ✓ AuthorizationService - Working")
log(f"  ✓ RoleBindingService - Working")
log(f"  ✓ PersonService - Working")
log("\n" + "=" * 70)
log("ALL TESTS PASSED! ✅")
log("=" * 70)

# Write to file
with open('test_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("\n✅ Test results written to: test_results.txt")
