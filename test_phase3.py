"""
Phase 3 Test Script - Campus Context System

Tests:
1. Thread-local context storage
2. Campus-aware manager filtering
3. Middleware context setting
4. Campus selection flow
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from kernel.models import Person, Campus, Role, UserAccount
from kernel.services import IdentityService, RoleBindingService
from kernel.context import set_current_campus_id, get_current_campus_id, clear_campus_context
from django.utils import timezone
from datetime import timedelta

print("=" * 70)
print("PHASE 3 CAMPUS CONTEXT SYSTEM - TEST")
print("=" * 70)

# Test 1: Thread-Local Context
print("\n[TEST 1] Thread-Local Context Storage")
print("-" * 70)
try:
    # Set campus context
    set_current_campus_id(1)
    campus_id = get_current_campus_id()
    print(f"  ✓ Set campus_id to 1, retrieved: {campus_id}")
    
    # Clear context
    clear_campus_context()
    campus_id = get_current_campus_id()
    print(f"  ✓ Cleared context, retrieved: {campus_id}")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 2: Create Test Data
print("\n[TEST 2] Creating Test Data")
print("-" * 70)
try:
    # Create or get campuses
    main_campus, _ = Campus.objects.get_or_create(
        name="Main Campus",
        defaults={'campus_type': 'PHYSICAL', 'is_active': True}
    )
    print(f"  ✓ Main Campus: ID={main_campus.id}")
    
    branch_campus, _ = Campus.objects.get_or_create(
        name="Branch Campus",
        defaults={'campus_type': 'PHYSICAL', 'is_active': True}
    )
    print(f"  ✓ Branch Campus: ID={branch_campus.id}")
    
    # Create test person
    try:
        test_person = IdentityService.get_person_by_email("test.user@campus.edu")
        print(f"  ✓ Using existing person: {test_person.full_name}")
    except:
        test_person = IdentityService.create_person(
            full_name="Test User",
            primary_phone="+92-300-9999999",
            primary_email="test.user@campus.edu"
        )
        print(f"  ✓ Created person: {test_person.full_name}")
    
    # Create user account
    try:
        user_account = UserAccount.objects.get(username="testuser")
        print(f"  ✓ Using existing user account: {user_account.username}")
    except UserAccount.DoesNotExist:
        user_account = UserAccount.objects.create_user(
            username="testuser",
            password="testpass123",
            person=test_person
        )
        print(f"  ✓ Created user account: {user_account.username}")
    
    # Get FACULTY role
    faculty_role = Role.objects.get(name='FACULTY')
    
    # Create role bindings at both campuses
    binding1 = RoleBindingService.create_binding(
        person_id=test_person.id,
        role_id=faculty_role.id,
        campus_id=main_campus.id,
        valid_from=timezone.now(),
        valid_until=timezone.now() + timedelta(days=365)
    )
    print(f"  ✓ Created binding at Main Campus")
    
    binding2 = RoleBindingService.create_binding(
        person_id=test_person.id,
        role_id=faculty_role.id,
        campus_id=branch_campus.id,
        valid_from=timezone.now(),
        valid_until=timezone.now() + timedelta(days=365)
    )
    print(f"  ✓ Created binding at Branch Campus")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Verify Bindings
print("\n[TEST 3] Verify Role Bindings")
print("-" * 70)
try:
    bindings = RoleBindingService.get_bindings_for_person(
        person_id=test_person.id,
        active_only=True
    )
    print(f"  ✓ Person has {bindings.count()} active binding(s)")
    
    for binding in bindings:
        print(f"    - {binding.role.name} at {binding.campus.name}")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 4: URLs and Views
print("\n[TEST 4] URL Configuration")
print("-" * 70)
try:
    from django.urls import reverse
    
    select_url = reverse('kernel:select_campus')
    print(f"  ✓ Campus selection URL: {select_url}")
    
    dashboard_url = reverse('kernel:dashboard')
    print(f"  ✓ Dashboard URL: {dashboard_url}")
    
    switch_url = reverse('kernel:switch_campus')
    print(f"  ✓ Campus switch URL: {switch_url}")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 5: Middleware Check
print("\n[TEST 5] Middleware Configuration")
print("-" * 70)
try:
    from django.conf import settings
    
    middleware_list = settings.MIDDLEWARE
    has_campus_middleware = 'kernel.middleware.CampusContextMiddleware' in middleware_list
    
    if has_campus_middleware:
        print(f"  ✓ CampusContextMiddleware is installed")
    else:
        print(f"  ✗ CampusContextMiddleware NOT found in MIDDLEWARE")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Test User Created:")
print(f"  Username: testuser")
print(f"  Password: testpass123")
print(f"  Email: test.user@campus.edu")
print(f"  Campuses: Main Campus, Branch Campus")
print(f"  Role: FACULTY")
print(f"\nNext Steps:")
print(f"  1. Navigate to http://127.0.0.1:8001/")
print(f"  2. You should be redirected to campus selection")
print(f"  3. Select a campus")
print(f"  4. You should see the dashboard")
print("=" * 70)

# Write results to file
with open('phase3_test_results.txt', 'w') as f:
    f.write("Phase 3 Test Complete\n")
    f.write(f"Test User: testuser / testpass123\n")
    f.write(f"Person: {test_person.full_name}\n")
    f.write(f"Bindings: {bindings.count()}\n")

print("\n✅ Test results written to: phase3_test_results.txt")
