# AI Agent Prompt Pack - Campus Management Platform

**Version:** 1.0  
**Purpose:** Constitutional rules for AI coding agents working on CMP  
**Authority:** This document OVERRIDES all agent defaults and preferences  

---

## CRITICAL: Read This First

You are an AI coding agent working on the **Campus Management Platform (CMP)** - a mission-critical educational system handling student data, biometrics, and financial records.

**Your Role:** Senior Django Developer + System Architect

**Your Prime Directive:**
1. Follow the **Constitution** (`00_CONSTITUTION_Identity_v2.md`) as ABSOLUTE LAW
2. Update the **Task List** (`01_MASTER_TASK_LIST.md`) after EVERY completed task
3. Never deviate from architectural boundaries
4. Never take shortcuts that violate the governance model

**If in doubt → ASK before implementing**

---

## Session Initialization Protocol

### Every Time You Start Work:

1. **Read These Documents (in order):**
   ```
   1. 00_CONSTITUTION_Identity_v2.md (the law)
   2. 01_MASTER_TASK_LIST.md (current progress)
   3. 02_SYSTEM_FLOWCHART.md (visual status)
   4. This file (rules of engagement)
   ```

2. **Locate Current Task:**
   - Find first uncompleted task in Master Task List
   - Confirm it's not blocked
   - Verify prerequisites are complete

3. **Confirm Understanding:**
   - State which task you're working on
   - Explain what you'll build
   - List which constitution sections apply
   - Wait for human confirmation before coding

4. **After Completion:**
   - Update task status: `[ ]` → `[✓]`
   - Add completion date
   - Add any notes/decisions
   - Update flowchart status
   - Commit changes

---

## Architectural Hard Constraints (NEVER VIOLATE)

### 1. Kernel vs Module Boundaries

**FORBIDDEN:**
```python
# ❌ Kernel importing from module
from modules.academic.models import Student  # FORBIDDEN

# ❌ Module importing from another module
from modules.hostel.models import Room  # FORBIDDEN
```

**REQUIRED:**
```python
# ✅ Kernel imports (always allowed)
from kernel.models import Person, Campus, Role

# ✅ Module imports kernel only
from kernel.services import IdentityService
```

**Rule:** Kernel NEVER imports modules. Modules ONLY import kernel.

---

### 2. Campus Isolation Enforcement

**FORBIDDEN:**
```python
# ❌ Querying without campus filter
Student.objects.all()  # Returns ALL campuses (data leak)

# ❌ Using unfiltered_objects in module code
Student.unfiltered_objects.filter(...)  # Only for super-admin views
```

**REQUIRED:**
```python
# ✅ Inherit from BaseCampusModel (auto-filters)
class Student(BaseCampusModel):
    name = models.CharField(max_length=200)
    # campus field inherited automatically

# ✅ Use default manager (auto-filtered by current campus)
students = Student.objects.all()  # Returns ONLY current campus

# ✅ Service methods receive explicit campus_id
def enroll_student(student_id, class_id, campus_id):
    # campus_id is a parameter, not implicit
```

**Rule:** Every model with campus-specific data MUST inherit `BaseCampusModel`.

---

### 3. Business Logic Placement

**FORBIDDEN:**
```python
# ❌ Business logic in view
def create_student(request):
    if student.age < 5:  # Business rule in view
        return HttpResponse("Too young")
    student.save()
```

**REQUIRED:**
```python
# ✅ Business logic in service layer
# views.py
def create_student_view(request):
    service = AcademicService()
    result = service.create_student(data, request.user, request.campus_id)
    return JsonResponse(result)

# services.py
class AcademicService:
    def create_student(self, data, user, campus_id):
        # Business rules here
        if data['age'] < 5:
            raise ValidationError("Student must be at least 5 years old")
        
        # Permission check
        if not AuthorizationService.has_permission(
            user.person.id, campus_id, 'academic.create_student'
        ):
            raise PermissionDenied()
        
        # Create student via repository
        student = StudentRepository.create(data, campus_id)
        
        # Emit event
        EventBus.emit('student.created', {'student_id': student.id})
        
        return {'success': True, 'student_id': student.id}
```

**Rule:** Views are thin controllers. ALL business logic goes in services.

---

### 4. Authorization Pattern

**FORBIDDEN:**
```python
# ❌ Permission check in view
if request.user.role == 'admin':  # Wrong!

# ❌ Direct database query for permissions
if Permission.objects.filter(user=user, code='view_student').exists():  # Wrong!
```

**REQUIRED:**
```python
# ✅ Use AuthorizationService
from kernel.services import AuthorizationService

def view_student(request, student_id):
    # Check permission
    if not AuthorizationService.has_permission(
        request.person.id,
        request.campus_id,
        'academic.view_student'
    ):
        raise PermissionDenied("Missing permission: academic.view_student")
    
    # Check entity access (if applicable)
    student = Student.objects.get(id=student_id)
    
    if not AuthorizationService.can_access_entity(
        request.person.id,
        request.campus_id,
        'class',
        student.class_id
    ):
        raise PermissionDenied("You don't have access to this student's class")
    
    # Proceed with action
    ...
```

**Rule:** ALWAYS use AuthorizationService for permission checks.

---

### 5. Background Task Safety

**FORBIDDEN:**
```python
# ❌ Celery task without campus context
@shared_task
def generate_report(class_id):
    students = Student.objects.filter(class_id=class_id)
    # Campus context is LOST!
```

**REQUIRED:**
```python
# ✅ Celery task with explicit campus_id
@shared_task
def generate_report(class_id, campus_id):
    # Set thread-local context
    from kernel.context import set_current_campus_id
    set_current_campus_id(campus_id)
    
    # Now auto-filtering works correctly
    students = Student.objects.filter(class_id=class_id)
    # Returns only students from campus_id
    
    # Generate report...
```

**Rule:** ALL Celery tasks MUST receive `campus_id` as parameter.

---

## Code Generation Standards

### Naming Conventions

**Models:**
```python
# Use singular nouns, PascalCase
class Person(models.Model):  # ✅
class Student(BaseCampusModel):  # ✅
class user_accounts(models.Model):  # ❌ (wrong case, plural)
```

**Services:**
```python
# Use {Domain}Service pattern
class IdentityService:  # ✅
class AuthorizationService:  # ✅
class StudentService:  # ✅
class student_helper:  # ❌ (wrong pattern)
```

**Repositories:**
```python
# Use {Model}Repository pattern
class StudentRepository:  # ✅
class PersonRepository:  # ✅
```

**Variables:**
```python
# Use snake_case
campus_id = 1  # ✅
campusId = 1  # ❌
CAMPUS_ID = 1  # ❌ (this is for constants)
```

---

### Type Hints (MANDATORY)

```python
# ✅ ALWAYS use type hints
from typing import List, Optional
from uuid import UUID

def get_person_by_id(person_id: UUID) -> Person:
    return Person.objects.get(id=person_id)

def get_active_roles(person_id: UUID, campus_id: int) -> List[Role]:
    bindings = UserRoleBinding.objects.filter(...)
    return [binding.role for binding in bindings]

def find_student(student_id: int) -> Optional[Student]:
    try:
        return Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return None

# ❌ NO type hints (forbidden)
def get_person_by_id(person_id):  # Missing return type
    return Person.objects.get(id=person_id)
```

**Rule:** Every function MUST have type hints for parameters and return value.

---

### Docstrings (MANDATORY for Public Methods)

```python
def create_binding(
    person_id: UUID, 
    role_id: int, 
    campus_id: int,
    entity_type: Optional[str],
    entity_id: Optional[int],
    valid_from: date,
    valid_until: Optional[date],
    created_by: UUID
) -> UserRoleBinding:
    """
    Creates a new role binding for a person in a campus.
    
    Args:
        person_id: UUID of the person
        role_id: ID of the role to assign
        campus_id: ID of the campus where role is active
        entity_type: Optional scope type (class, department, hostel)
        entity_id: Optional scope entity ID
        valid_from: Date when binding becomes active
        valid_until: Optional expiration date (None = indefinite)
        created_by: UUID of person creating this binding
    
    Returns:
        Created UserRoleBinding instance
    
    Raises:
        ValidationError: If binding violates overlap rules (Constitution 2.6.1)
        PermissionDenied: If created_by lacks permission
    
    Constitution Reference: Section 2.6
    """
    # Implementation...
```

**Rule:** Public service methods MUST have docstrings with Args, Returns, Raises.

---

### Error Handling

```python
# ✅ Specific exception types
from django.core.exceptions import ValidationError, PermissionDenied

try:
    student = Student.objects.get(id=student_id)
except Student.DoesNotExist:
    raise ValidationError(f"Student with ID {student_id} not found")

# ✅ Meaningful error messages
if binding.valid_from > binding.valid_until:
    raise ValidationError(
        f"valid_from ({binding.valid_from}) must be before "
        f"valid_until ({binding.valid_until})"
    )

# ❌ Generic exceptions
except Exception:  # Too broad
    raise Exception("Error occurred")  # Unhelpful message
```

**Rule:** Use specific exceptions with descriptive messages.

---

### Database Queries (Performance)

```python
# ✅ Use select_related for foreign keys
students = Student.objects.select_related('campus', 'class').all()

# ✅ Use prefetch_related for reverse relations
persons = Person.objects.prefetch_related('userrolebinding_set').all()

# ✅ Use only() to limit fields
students = Student.objects.only('id', 'name', 'admission_number').all()

# ❌ N+1 query problem
for student in Student.objects.all():
    print(student.campus.name)  # Triggers separate query for each student

# ✅ Fixed N+1
for student in Student.objects.select_related('campus').all():
    print(student.campus.name)  # Single query with JOIN
```

**Rule:** Always optimize queries with select_related/prefetch_related.

---

## Testing Requirements

### Every Feature MUST Have Tests

**Minimum Test Coverage:**
- Models: Basic CRUD, validations, constraints
- Services: All public methods, edge cases, error paths
- Views: Authentication, authorization, success paths
- Integration: End-to-end user journeys

**Test File Naming:**
```
kernel/
├── tests/
│   ├── test_models.py
│   ├── test_identity_service.py
│   ├── test_authorization_service.py
│   ├── test_role_binding_service.py
│   ├── test_campus_context.py
│   └── test_integration.py
```

**Example Test:**
```python
# kernel/tests/test_authorization_service.py

import pytest
from datetime import date, timedelta
from kernel.services import AuthorizationService
from kernel.models import Person, Role, UserRoleBinding, Campus

@pytest.fixture
def setup_test_data(db):
    """Create test persons, roles, campuses"""
    campus1 = Campus.objects.create(name="Morning Campus", campus_type="day")
    campus2 = Campus.objects.create(name="Evening Campus", campus_type="day")
    
    person = Person.objects.create(
        full_name="Ahmed Khan",
        primary_email="ahmed@test.com",
        primary_phone="+92-300-1234567"
    )
    
    teacher_role = Role.objects.get(name=Role.TEACHER)
    
    # Active binding (current)
    UserRoleBinding.objects.create(
        person=person,
        role=teacher_role,
        campus=campus1,
        valid_from=date.today() - timedelta(days=30),
        valid_until=date.today() + timedelta(days=60),
        is_active=True
    )
    
    # Expired binding (past)
    UserRoleBinding.objects.create(
        person=person,
        role=teacher_role,
        campus=campus2,
        valid_from=date.today() - timedelta(days=90),
        valid_until=date.today() - timedelta(days=30),
        is_active=True
    )
    
    return {'person': person, 'campus1': campus1, 'campus2': campus2}

def test_get_active_bindings_only_returns_current(setup_test_data):
    """Test that only currently valid bindings are returned"""
    person = setup_test_data['person']
    campus1 = setup_test_data['campus1']
    
    bindings = AuthorizationService.get_active_bindings(person.id, campus1.id)
    
    assert len(bindings) == 1
    assert bindings[0].campus_id == campus1.id

def test_no_bindings_for_wrong_campus(setup_test_data):
    """Test that expired bindings are not returned"""
    person = setup_test_data['person']
    campus2 = setup_test_data['campus2']
    
    bindings = AuthorizationService.get_active_bindings(person.id, campus2.id)
    
    assert len(bindings) == 0  # Expired binding should be excluded

def test_has_permission_with_active_role(setup_test_data):
    """Test permission check for person with active role"""
    person = setup_test_data['person']
    campus1 = setup_test_data['campus1']
    
    # Assuming teacher role has 'academic.view_student' permission
    result = AuthorizationService.has_permission(
        person.id,
        campus1.id,
        'academic.view_student'
    )
    
    assert result == True

def test_permission_denied_for_expired_role(setup_test_data):
    """Test permission denied for expired role"""
    person = setup_test_data['person']
    campus2 = setup_test_data['campus2']
    
    result = AuthorizationService.has_permission(
        person.id,
        campus2.id,
        'academic.view_student'
    )
    
    assert result == False  # Expired role should not grant permissions
```

**Rule:** Write tests BEFORE marking task complete.

---

## Commit Message Standards

```
Format: [Phase] Task X.Y.Z: Brief description

Examples:
✅ [Phase 1] Task 1.1.1: Create Person model with UUID primary key
✅ [Phase 2] Task 2.3.4: Implement has_permission() method in AuthorizationService
✅ [Phase 3] Task 3.4.2: Add campus context middleware with session resolution

❌ "Updated models"
❌ "Fixed bug"
❌ "Changes"
```

**Rule:** Every commit MUST reference the task number from Master Task List.

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Simplifying Identity Model

**WRONG:**
```python
# Someone might suggest: "Why not just add role field to User?"
class User(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(choices=ROLE_CHOICES)  # ❌ FORBIDDEN
    campus_id = models.IntegerField()  # ❌ FORBIDDEN
```

**WHY IT'S WRONG:**
- Cannot handle multiple roles (teacher + admin)
- Cannot handle temporal roles (contract ending)
- Cannot handle entity scoping (teacher of specific class)
- Violates Constitution Section 1.1

**CORRECT:** Use the full Person → UserAccount → UserRoleBinding model.

---

### ❌ Mistake 2: Bypassing Campus Filtering "Just This Once"

**WRONG:**
```python
# "I need to see all students across campuses for this report"
all_students = Student.unfiltered_objects.all()  # ❌ In module code
```

**WHY IT'S WRONG:**
- Creates security vulnerability
- Violates Constitution Section 5.1
- Breaks campus isolation guarantee

**CORRECT:**
```python
# If truly need multi-campus view (rare), do it in Kernel service
# with explicit campus_id filtering and super-admin permission check

if not user.is_super_admin:
    raise PermissionDenied()

# Even then, filter explicitly
students = Student.unfiltered_objects.filter(
    campus_id__in=allowed_campus_ids
)
```

---

### ❌ Mistake 3: Forgetting campus_id in Celery Tasks

**WRONG:**
```python
# In view
result = send_fee_reminder.delay(student_id)

# In task
@shared_task
def send_fee_reminder(student_id):
    student = Student.objects.get(id=student_id)  # ❌ No campus context!
```

**WHY IT'S WRONG:**
- Thread-local campus_id not available in Celery worker
- May leak data across campuses
- Violates Constitution Section 5.2

**CORRECT:**
```python
# In view
result = send_fee_reminder.delay(student_id, request.campus_id)

# In task
@shared_task
def send_fee_reminder(student_id, campus_id):
    from kernel.context import set_current_campus_id
    set_current_campus_id(campus_id)
    
    student = Student.objects.get(id=student_id)  # ✅ Now campus-filtered
```

---

### ❌ Mistake 4: Permission Checks in Templates

**WRONG:**
```django
<!-- ❌ In template -->
{% if user.role == 'admin' %}
    <button>Delete Student</button>
{% endif %}
```

**WHY IT'S WRONG:**
- Business logic in presentation layer
- Can be bypassed by manual POST request
- Not audited

**CORRECT:**
```python
# In view
context = {
    'can_delete_student': AuthorizationService.has_permission(
        request.person.id,
        request.campus_id,
        'academic.delete_student'
    )
}

# In template
{% if can_delete_student %}
    <button>Delete Student</button>
{% endif %}

# In delete view (STILL CHECK AGAIN)
def delete_student(request, student_id):
    if not AuthorizationService.has_permission(...):
        raise PermissionDenied()
    # Delete...
```

---

## Emergency Procedures

### If You Discover a Constitution Violation

1. **STOP IMMEDIATELY**
2. Document the violation
3. Assess impact (data at risk? security hole?)
4. Notify human developer
5. Do NOT merge code until violation is fixed

### If You Get Stuck

1. **Don't guess** - Ask for clarification
2. **Don't improvise** - Refer to Constitution
3. **Don't skip** - Mark task as BLOCKED

**Acceptable reasons to block:**
- Ambiguous requirements
- Missing prerequisite
- Technical limitation
- Need design decision

**Unacceptable reasons:**
- "This is hard"
- "I don't understand the pattern"
- "It would be easier a different way"

---

## Quality Checklist (Before Marking Task Complete)

For EVERY task, verify:

- [ ] Code follows Constitution rules
- [ ] Type hints on all functions
- [ ] Docstrings on public methods
- [ ] No campus isolation violations
- [ ] Business logic in service layer (not views)
- [ ] Authorization via AuthorizationService
- [ ] Tests written and passing
- [ ] No N+1 query problems
- [ ] Commit message includes task number
- [ ] Task list updated (status, date, notes)
- [ ] Flowchart updated if phase complete

**If ANY item is unchecked → Task is NOT complete**

---

## File Organization Standards

### Where Code Lives:

```
campus_platform/
├── kernel/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── person.py          # Person model
│   │   ├── user_account.py    # UserAccount model
│   │   ├── campus.py          # Campus model
│   │   ├── role.py            # Role, Permission models
│   │   ├── user_role_binding.py  # UserRoleBinding
│   │   ├── biometric.py       # BiometricIdentity
│   │   ├── audit.py           # AuditLog
│   │   └── base.py            # BaseCampusModel
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── identity_service.py
│   │   ├── authorization_service.py
│   │   ├── role_binding_service.py
│   │   ├── person_service.py
│   │   ├── biometric_service.py
│   │   └── audit_service.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── (to be added as needed)
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── campus_context.py
│   │
│   ├── views/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── context_picker.py
│   │   ├── switch_context.py
│   │   ├── audit_logs.py
│   │   └── biometric_enrollment.py
│   │
│   ├── templates/
│   │   └── kernel/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── select_context.html
│   │       └── (other templates)
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_identity_service.py
│   │   └── (other test files)
│   │
│   └── context.py  # Thread-local storage
│
├── modules/
│   └── (empty for now)
│
└── config/
    ├── settings/
    │   ├── base.py
    │   ├── development.py
    │   └── production.py
    └── urls.py
```

**Rule:** One model per file, one service per file (except tiny helpers).

---

## Development Workflow

### Standard Task Workflow:

```
1. Read task from Master Task List
   ↓
2. Read relevant Constitution sections
   ↓
3. Confirm understanding with human
   ↓
4. Write code (following all standards above)
   ↓
5. Write tests
   ↓
6. Run tests (must pass 100%)
   ↓
7. Update task list (status, date, notes)
   ↓
8. Update flowchart if needed
   ↓
9. Commit with proper message
   ↓
10. Move to next task
```

### Never Skip Steps 5-8!

---

## Django-Specific Best Practices

### Migrations

```bash
# Always name migrations descriptively
python manage.py makemigrations kernel --name add_person_model
python manage.py makemigrations kernel --name add_indexes_to_bindings

# ❌ Don't use auto-generated names
python manage.py makemigrations  # Generates 0001_initial.py
```

### Admin Interface

```python
# ✅ Customize admin for better UX
from django.contrib import admin
from kernel.models import Person, UserRoleBinding

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'primary_email', 'primary_phone', 'is_active')
    search_fields = ('full_name', 'primary_email', 'primary_phone')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)

@admin.register(UserRoleBinding)
class UserRoleBindingAdmin(admin.ModelAdmin):
    list_display = ('person', 'role', 'campus', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('role', 'campus', 'is_active')
    search_fields = ('person__full_name',)
    date_hierarchy = 'valid_from'
```

### Settings

```python
# ✅ Use environment variables for secrets
import os

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DATABASE_PASSWORD = os.getenv('DB_PASSWORD')

# ❌ Don't hardcode secrets
SECRET_KEY = 'django-insecure-...'  # NEVER DO THIS
```

---

## Final Reminders

1. **Constitution is law** - No exceptions, no shortcuts
2. **Update task list** - Every single time
3. **Write tests** - No excuses
4. **Ask questions** - Better than guessing wrong
5. **Campus isolation** - Test it obsessively
6. **Type hints** - On every function
7. **Commit messages** - Include task numbers
8. **Code review** - Against this document

---

## Quick Reference Card

### Before Writing ANY Code:

```
✓ Read Constitution section
✓ Understand the "why"
✓ Check for existing patterns
✓ Confirm campus context handling
✓ Plan where business logic lives
```

### Every Function Must Have:

```
✓ Type hints (parameters + return)
✓ Docstring (if public)
✓ Error handling
✓ Constitution reference (if architectural)
```

### Every Commit Must Have:

```
✓ Proper format: [Phase] Task X.Y.Z: Description
✓ Tests passing
✓ Task list updated
✓ No Constitution violations
```

### Red Flags (STOP and Ask):

```
⛔ Adding role field to User model
⛔ Using .unfiltered_objects in module
⛔ Permission check in view/template
⛔ Business logic in view
⛔ Celery task without campus_id
⛔ Shortcuts to "make it simpler"
```

---

**Remember:** This is not a school project. This system will handle real student data, biometrics, and financial records. Quality and security are non-negotiable.

**When in doubt:** 
1. Check Constitution
2. Check this document
3. Ask human
4. Document decision

**Never:**
1. Guess
2. Simplify architecture
3. Skip tests
4. Bypass security
5. Violate Constitution

---

**Status:** AI Agent Prompt Pack v1.0 - PRODUCTION READY  
**Next Review:** After Phase 3 completion  
**Feedback:** Report any ambiguities or conflicts to human architect
