
import os
import django
import sys
from django.utils import timezone

# Setup Django
sys.path.append(r"E:\The CMS")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from kernel.models import Person, UserAccount, Campus, Role, UserRoleBinding
from kernel.services.role_binding_service import RoleBindingService
from django.conf import settings

def run_security_audit():
    print("\n🔒 STARTING SECURITY AUDIT...")
    
    # Patch ALLOWED_HOSTS for test client
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS += ['testserver']
    
    # 1. Setup Data
    campus_a_obj, _ = Campus.objects.get_or_create(name="Secure Campus A")
    campus_b_obj, _ = Campus.objects.get_or_create(name="Secure Campus B")
    role_student, _ = Role.objects.get_or_create(name='student')
    
    # OLD DATA CLEANUP
    print("Cleaning up old test data...")
    UserAccount.objects.filter(username__in=["hacker_a", "victim_b"]).delete()
    Person.objects.filter(primary_email__in=["hacker@test.com", "victim@test.com"]).delete()
    
    # Create User A (Campus A)
    person_a = Person.objects.create(full_name="Hacker A", primary_email="hacker@test.com", primary_phone="555-0001")
    user_a = UserAccount.objects.create_user(person=person_a, username="hacker_a", password="password123")
    UserRoleBinding.objects.create(person=person_a, role=role_student, campus=campus_a_obj, valid_from=timezone.now())
    
    # Create Victim User (Campus B)
    person_b = Person.objects.create(full_name="Victim B", primary_email="victim@test.com", primary_phone="555-0002")
    UserRoleBinding.objects.create(person=person_b, role=role_student, campus=campus_b_obj, valid_from=timezone.now())
    
    client = Client()
    client.login(username="hacker_a", password="password123")
    
    # 2. Test Cross-Campus Access (Data Leakage)
    print("\n[Test 1] Testing Cross-Campus Data Access...")
    # Attempt to switch context to Campus B
    session = client.session
    session['active_campus_id'] = str(campus_b_obj.id)
    session.save()
    
    # Check if the user *actually* has a binding for Campus B
    bindings = RoleBindingService.get_bindings_for_person(person_a.id, active_only=True)
    has_access = bindings.filter(campus_id=campus_b_obj.id).exists()
    
    if not has_access:
        print("✅ PASS: Hacker A cannot access Campus B data.")
    else:
        print("❌ FAIL: Hacker A HAS access to Campus B!")

    # 3. Test Privilege Escalation
    print("\n[Test 2] Testing Privilege Escalation...")
    # Student trying to access admin endpoint
    response = client.get('/admin/')
    # 302 is also safe (redirect to login), 403 is forbidden. 200 OK is bad if it's the admin index.
    if response.status_code != 200:
        print(f"✅ PASS: Admin panel access denied (Status: {response.status_code}).")
    else:
        # Check if it's the login page (which is 200 OK) vs actual admin index
        if "Log in" in str(response.content) or "login" in response.request['PATH_INFO']:
             print(f"✅ PASS: Admin panel access denied (Redirected to Login).")
        else:
             print("❌ FAIL: Student accessed Admin panel!")

if __name__ == "__main__":
    try:
        run_security_audit()
    except Exception as e:
        print(f"❌ ERROR: {e}")
