# Universal Identity & Access Control Constitution

## Version 2.0 - Production Implementation Ready

**Status:** FINAL - This is the constitutional law for identity in CMP  
**Authority:** This document overrides all other identity-related decisions  
**Enforcement:** AI agents MUST NOT deviate from these rules  

---

## 0. Purpose of This Document

This document defines the **Universal Identity Model** for the Campus Management Platform (CMP).

It exists to:

* Eliminate ambiguity around users, roles, and permissions
* Support multi-campus, multi-role, and temporal access
* Be safe for AI coding agents to implement without interpretation
* Serve as the **final authority** on identity-related decisions

**This document is kernel law. Modules must comply.**

---

## 1. Core Identity Philosophy

### 1.1 Fundamental Principles

1. **A Person is not a Role**
2. **A Role is not a Permission**
3. **A User Account is not Campus-bound**
4. **Access is always Contextual (Campus + Role + Time)**

**Identity is stable. Access is dynamic.**

### 1.2 The Separation of Concerns

```
Person (WHO)
  ↓ has credentials
UserAccount (HOW they authenticate)
  ↓ activates
UserRoleBinding (WHAT they can do, WHERE, WHEN)
  ↓ grants
Permissions (WHICH actions are allowed)
```

---

## 2. Core Identity Objects (Canonical Models)

### 2.1 Person (Immutable Identity)

Represents a real human being.

**Properties:**

```python
id: UUID (primary key)
full_name: string
date_of_birth: date (optional)
primary_email: string (unique, nullable)
primary_phone: string (unique)
created_at: timestamp
is_active: boolean
```

**Rules:**

* One Person exists across the entire college installation
* Person is **never deleted** (only deactivated via `is_active=false`)
* Biometric and hardware identities attach here
* Email and phone are for contact, NOT authentication
* Person records are **immutable** after creation (except is_active)

**Lifecycle:**
* Created during admission/hiring
* Deactivated when leaving institution
* Reactivated if person returns
* Historical data preserved indefinitely

---

### 2.2 UserAccount (Authentication Shell)

Represents a login credential set.

**Properties:**

```python
id: bigint (primary key)
person_id: UUID (foreign key → Person)
username: string (unique)
email: string (unique)
password_hash: string
last_login: timestamp (nullable)
is_locked: boolean (default: false)
failed_login_attempts: int (default: 0)
lockout_until: timestamp (nullable)
created_at: timestamp
```

**Rules:**

* One Person may have **multiple UserAccounts** (rare: e.g., personal + admin account)
* Authentication ≠ Authorization
* UserAccount contains **NO role or campus logic**
* Locking a UserAccount does NOT affect Person's other accounts
* Password resets update this table only

**Security:**
* Passwords hashed using Django's PBKDF2 (default)
* Max 5 failed login attempts → 15-minute lockout
* Lockout resets on successful login

---

### 2.3 Role (Semantic Meaning)

Represents a named responsibility.

**Predefined Roles:**

```python
STUDENT = 'student'
TEACHER = 'teacher'
ADMIN = 'admin'
PRINCIPAL = 'principal'
PARENT = 'parent'
WARDEN = 'warden'
LIBRARIAN = 'librarian'
ACCOUNTANT = 'accountant'
TRANSPORT_MANAGER = 'transport_manager'
```

**Properties:**

```python
id: int (primary key)
name: string (unique, from choices above)
description: string
is_system_role: boolean (true for predefined roles)
created_at: timestamp
```

**Rules:**

* System roles (is_system_role=true) are **kernel-defined and immutable**
* Modules may **reference** roles but **CANNOT redefine** them
* Custom roles (is_system_role=false) may be added by college admins (future feature)
* Deleting a role requires migrating all existing bindings first

---

### 2.4 Permission (Atomic Capability)

Represents a single allowed action.

**Examples:**

```python
# Academic Module
'academic.view_student'
'academic.edit_student'
'academic.mark_attendance'
'academic.view_grades'
'academic.enter_grades'

# Finance Module
'finance.view_fees'
'finance.collect_payment'
'finance.generate_invoice'
'finance.approve_refund'

# Hostel Module
'hostel.view_rooms'
'hostel.allocate_room'
'hostel.manage_mess_menu'

# Kernel Permissions
'kernel.manage_users'
'kernel.manage_roles'
'kernel.view_audit_logs'
```

**Properties:**

```python
id: int (primary key)
code: string (unique, namespaced with module)
name: string (human-readable)
module: string (academic, finance, hostel, kernel)
description: string
is_dangerous: boolean (requires extra confirmation)
created_at: timestamp
```

**Naming Convention:**
* Format: `{module}.{action}_{resource}`
* Examples: `academic.view_student`, `finance.approve_refund`
* Dangerous permissions: `kernel.delete_all_data`, `finance.bypass_approval`

**Rules:**

* Permissions are **kernel-defined or module-defined**
* Modules **register** their permissions during installation
* Permission codes are **immutable** after creation
* Modules cannot invent permissions at runtime

---

### 2.5 RolePermissionMap

Defines which permissions belong to which roles.

**Properties:**

```python
id: int (primary key)
role_id: int (foreign key → Role)
permission_id: int (foreign key → Permission)
granted_by: UUID (foreign key → Person, nullable)
created_at: timestamp
```

**Rules:**

* Many-to-many relationship (one role has many permissions)
* Changes are audited (who granted/revoked)
* System role mappings are seeded during installation
* Custom mappings can be added by college admins

**Default Mappings (Seeded):**

```python
Teacher Role:
  - academic.view_student
  - academic.mark_attendance
  - academic.enter_grades
  - academic.view_timetable

Admin Role:
  - academic.* (all academic permissions)
  - finance.view_fees
  - hostel.view_rooms
  - kernel.manage_users

Principal Role:
  - *.* (all permissions except dangerous ones)
```

---

### 2.6 UserRoleBinding (The Heart of the System)

Defines **who can do what, where, and when**.

**Properties:**

```python
id: bigint (primary key)
person_id: UUID (foreign key → Person)
role_id: int (foreign key → Role)
campus_id: int (foreign key → Campus)
entity_type: string (nullable: 'class', 'department', 'hostel_block')
entity_id: bigint (nullable: ID of the specific class/dept/hostel)
valid_from: date
valid_until: date (nullable, NULL = indefinite)
is_active: boolean (default: true)
created_at: timestamp
created_by: UUID (foreign key → Person)
deactivated_at: timestamp (nullable)
deactivated_by: UUID (foreign key → Person, nullable)
notes: text (nullable, reason for binding/revocation)
```

**Rules:**

* A Person may have **multiple active bindings** simultaneously
* Bindings are **campus-specific** (cannot span campuses)
* Bindings may **overlap in time** if rules allow (see section 2.6.1)
* Bindings are **never deleted** (auditable history)
* Deactivation sets `is_active=false` and records who/when

**Examples:**

```python
# Ahmed is a Teacher at Morning Campus for Class 10-A
{
  person_id: UUID('123...'),
  role_id: TEACHER,
  campus_id: 1,
  entity_type: 'class',
  entity_id: 15,  # Class 10-A
  valid_from: '2025-01-01',
  valid_until: '2025-06-30',
  is_active: true
}

# Ahmed is also Admin at Evening Campus (no entity scope)
{
  person_id: UUID('123...'),
  role_id: ADMIN,
  campus_id: 2,
  entity_type: null,
  entity_id: null,  # Campus-wide access
  valid_from: '2025-01-01',
  valid_until: null,  # Indefinite
  is_active: true
}
```

---

### 2.6.1 Binding Overlap Rules (Critical)

**Rule 1: Same (person, role, campus) with DIFFERENT entity scopes**

✅ **ALLOWED:**
```python
Binding 1: (Ahmed, Teacher, Campus 1, entity_id=15)  # Class 10-A
Binding 2: (Ahmed, Teacher, Campus 1, entity_id=20)  # Class 9-B

Result: Ahmed can teach both classes
```

**Rule 2: Same (person, role, campus) with SAME or NULL entity scope**

❌ **REJECTED:**
```python
Binding 1: (Ahmed, Teacher, Campus 1, entity_id=NULL, Jan-Jun)
Binding 2: (Ahmed, Teacher, Campus 1, entity_id=NULL, May-Dec)

Error: "Duplicate role binding - overlapping dates with same scope"
```

**Rule 3: Different roles are ALWAYS allowed**

✅ **ALLOWED:**
```python
Binding 1: (Ahmed, Teacher, Campus 1, Jan-Jun)
Binding 2: (Ahmed, Admin, Campus 1, May-Dec)

Result: Ahmed has both roles during May-June overlap
```

**Rule 4: Deactivation takes precedence**

```python
If is_active=false, binding is ignored regardless of valid_from/valid_until
```

**Enforcement:**
* Validation happens at creation time (service layer)
* Database constraint: UNIQUE(person_id, role_id, campus_id, entity_id) WHERE is_active=true AND valid_until IS NULL
* Overlapping temporal bindings checked via service logic

---

## 3. Campus Context Resolution

### 3.1 Resolution Strategy (Hybrid – Mandatory)

The system uses a **Hybrid Context Model**:

* **Web Requests:** Campus resolved via middleware (automatic)
* **Service Layer:** Campus passed explicitly (explicit parameters)
* **Background Tasks:** Campus must be injected explicitly (Celery task parameter)

**No service method may rely on implicit global state.**

---

### 3.2 Middleware Responsibilities

**File:** `kernel/middleware/campus_context.py`

Middleware **MUST**:

1. Resolve active campus from (priority order):
   * URL parameter: `?campus_id=1`
   * Session state: `request.session['active_campus_id']`
   * User's default campus (most recent binding)

2. Attach `request.campus_id` for view access

3. Attach `request.person` (the Person object)

4. Attach `request.active_bindings` (currently valid bindings for this campus)

5. Store `campus_id` in thread-local context for ORM managers

**If campus cannot be resolved:**
* Redirect to `/kernel/select-context` (context picker UI)

**If person has no access to resolved campus:**
* Redirect to `/kernel/access-denied`

---

### 3.3 Context Selection & Switching

#### 3.3.1 First Login Flow

```
1. User authenticates (username + password)
2. System loads Person from UserAccount
3. System queries active UserRoleBindings for person_id
4. If SINGLE binding → Auto-select campus/role
5. If MULTIPLE bindings → Redirect to context picker
6. Selected context stored in session
7. User lands on dashboard
```

#### 3.3.2 Context Picker UI

**Required Elements:**
* List all active bindings (campus + role + entity if applicable)
* Show validity dates
* Highlight default/recommended context
* Allow selection
* "Remember this choice" checkbox (sets default)

**Example Display:**
```
Select Your Context:

[ ] Morning Campus - Teacher (Class 10-A)
    Valid: Jan 1, 2025 - Jun 30, 2025

[x] Evening Campus - Administrator
    Valid: Indefinite (Default)

[ ] Residential Campus - Warden (Boys Hostel Block-B)
    Valid: Jan 1, 2025 - Dec 31, 2025

[Continue]
```

#### 3.3.3 Context Switching (Mid-Session)

**UI Element:** Dropdown in header/navbar

```
Current Context: Evening Campus - Administrator [Switch ▼]

Dropdown Menu:
  → Morning Campus - Teacher (Class 10-A)
  → Residential Campus - Warden
  → [Manage Contexts]
```

**On Switch:**
1. Update session: `request.session['active_campus_id'] = new_campus_id`
2. Update session: `request.session['active_role_id'] = new_role_id`
3. Log event in audit log
4. Reload current page with new context filter

#### 3.3.4 Session Schema

```python
request.session = {
  'person_id': UUID('123...'),
  'active_campus_id': 1,
  'active_role_id': 5,
  'active_binding_id': 42,
  'active_entity_type': 'class',
  'active_entity_id': 15,
  'context_switched_at': '2025-02-10T14:30:00Z',
  'context_switch_count': 3  # Daily counter (rate limiting)
}
```

#### 3.3.5 URL Override (Admin Feature)

**Format:** `?campus_id=2&role_id=3`

**Purpose:**
* Troubleshooting (support team viewing user's context)
* Testing (QA simulating different contexts)
* Admin impersonation (with audit logging)

**Security:**
* Only college super-admins can use URL override
* Every override is logged to audit log
* Override is temporary (does NOT update session permanently)

---

## 4. Authorization Algorithm (Canonical)

### 4.1 Permission Check Process

To authorize an action:

```python
def can_perform_action(person_id, campus_id, permission_code):
    """
    Canonical authorization check
    
    Returns: (allowed: bool, reason: string)
    """
    
    # Step 1: Identify Person (already done via authentication)
    person = Person.objects.get(id=person_id)
    
    if not person.is_active:
        return (False, "Person is deactivated")
    
    # Step 2: Resolve active Campus (from request context)
    # campus_id passed explicitly
    
    # Step 3: Load active UserRoleBindings for (person, campus, time)
    today = timezone.now().date()
    bindings = UserRoleBinding.objects.filter(
        person_id=person_id,
        campus_id=campus_id,
        is_active=True,
        valid_from__lte=today
    ).filter(
        Q(valid_until__isnull=True) | Q(valid_until__gte=today)
    )
    
    if not bindings.exists():
        return (False, "No active role bindings for this campus")
    
    # Step 4: Aggregate permissions from all active roles
    permissions = set()
    for binding in bindings:
        role_perms = Permission.objects.filter(
            rolepermissionmap__role=binding.role
        ).values_list('code', flat=True)
        permissions.update(role_perms)
    
    # Step 5: Evaluate permission
    if permission_code in permissions:
        return (True, "Allowed")
    else:
        return (False, f"Missing permission: {permission_code}")
```

**Authorization is ADDITIVE:**
* If person has multiple roles, they get the **union** of all permissions
* Example: Teacher permissions + Admin permissions = Both sets combined

---

### 4.2 Entity Scope Resolution Rules

When checking if a person can access a specific entity (class, hostel, department):

**Rule 1: NULL entity_id (wildcard) beats specific entity_id**

```python
Bindings:
  1. (Teacher, campus_id=1, entity_id=15)  # Class 10-A
  2. (Admin, campus_id=1, entity_id=NULL)  # Campus-wide

Can access Class 10-B (entity_id=20)?
→ YES (Admin binding has NULL scope = all entities)
```

**Rule 2: Multiple specific scopes are ADDITIVE**

```python
Bindings:
  1. (Teacher, campus_id=1, entity_id=15)  # Class 10-A
  2. (Teacher, campus_id=1, entity_id=20)  # Class 10-B

Can access Class 10-A? → YES
Can access Class 10-B? → YES
Can access Class 9-C?  → NO
```

**Rule 3: Entity type must match**

```python
Binding: (Warden, campus_id=1, entity_type='hostel_block', entity_id=5)

Can access hostel_block 5? → YES
Can access class 10? → NO (wrong entity_type)
```

**Implementation:**

```python
def can_access_entity(person_id, campus_id, entity_type, entity_id):
    bindings = get_active_bindings(person_id, campus_id)
    
    for binding in bindings:
        # Wildcard access (no entity scope)
        if binding.entity_id is None:
            return True
        
        # Specific entity match
        if (binding.entity_type == entity_type and 
            binding.entity_id == entity_id):
            return True
    
    return False
```

---

## 5. Data Safety & Isolation

### 5.1 Campus-Aware Managers (Mandatory)

All campus-bound models **MUST**:

* Inherit from `BaseCampusModel`
* Use a default manager that auto-filters by `campus_id`
* Provide `.unfiltered_objects` manager for super-admin access

**Example:**

```python
# kernel/models/base.py

class CampusAwareManager(models.Manager):
    """Auto-filters queries by current campus context"""
    
    def get_queryset(self):
        campus_id = get_current_campus_id()  # From thread-local
        
        if campus_id is None:
            raise ImproperlyConfigured(
                "Campus context not set. Use middleware or pass campus_id explicitly."
            )
        
        return super().get_queryset().filter(campus_id=campus_id)

class BaseCampusModel(models.Model):
    """Base class for all campus-scoped data"""
    
    campus = models.ForeignKey('kernel.Campus', on_delete=models.CASCADE)
    
    objects = CampusAwareManager()        # Auto-filtered
    unfiltered_objects = models.Manager()  # Bypass (super-admin only)
    
    class Meta:
        abstract = True
```

**Usage in Modules:**

```python
# modules/academic/models.py

class Student(BaseCampusModel):
    name = models.CharField(max_length=200)
    # campus field inherited automatically

# Query behavior:
# If request.campus_id = 1
Student.objects.all()  # Returns ONLY campus_id=1 students (automatic)

# Super-admin can see all:
Student.unfiltered_objects.all()  # Returns students from ALL campuses
```

### 5.2 Background Task Safety

**Celery tasks MUST receive campus_id as parameter:**

```python
# ❌ DANGEROUS (no campus context)
@shared_task
def generate_report(class_id):
    students = Student.objects.filter(class_id=class_id)
    # Campus context is LOST in background task!

# ✅ SAFE (explicit campus parameter)
@shared_task
def generate_report(class_id, campus_id):
    # Set thread-local context
    _thread_locals.campus_id = campus_id
    
    students = Student.objects.filter(class_id=class_id)
    # Now auto-filtered correctly
```

---

## 6. Hardware & Biometric Identity

### 6.1 BiometricIdentity Model

**Properties:**

```python
id: UUID (primary key)
person_id: UUID (foreign key → Person)
biometric_type: enum ('fingerprint', 'face')
encoding: binary (encrypted template)
model_version: string (e.g., 'deepface_0.0.79', 'secugen_sdk_2.1')
quality_score: float (0.0 to 1.0)
enrollment_device_id: string (which scanner was used)
enrolled_by: UUID (foreign key → Person)
created_at: timestamp
is_active: boolean (default: true)
deactivated_at: timestamp (nullable)
deactivated_reason: string (nullable)
```

**Rules:**

* One Person may have multiple biometric identities (multiple fingers, face)
* Biometric data is **always encrypted at rest**
* `model_version` is **critical** - never compare across versions
* Deactivation does NOT delete data (audit trail)
* Old encodings remain for reference if model is upgraded

---

### 6.2 Biometric Enrollment Flow

**Scenario:** Registering student fingerprint during admission

```
1. Admin initiates enrollment
   → UI: "Register Fingerprint for Ahmed Khan"

2. System generates enrollment session
   → Session ID: ENC_12345
   → Links to person_id

3. Scanner captures biometric sample
   → Hardware Bridge (local app) communicates with USB scanner
   → Captures raw template data

4. Quality check
   → SDK validates quality score (must be >= 0.7)
   → If low quality → "Poor scan, please try again"

5. Generate encoding
   → Use DeepFace/SecuGen SDK
   → Encode template into fixed-length vector

6. Encrypt and store
   → Encrypt encoding using college's encryption key
   → Store in BiometricIdentity table:
     {
       person_id: UUID('123...'),
       biometric_type: 'fingerprint',
       encoding: <encrypted_binary>,
       model_version: 'secugen_sdk_2.1',
       quality_score: 0.92,
       enrollment_device_id: 'DEV_GATE_01',
       enrolled_by: <admin_person_id>
     }

7. Confirmation
   → UI: "Fingerprint registered successfully"
   → Test scan immediately to verify
```

---

### 6.3 Biometric Authentication Flow

**Scenario:** Ahmed scans fingerprint at gate for attendance

```
1. Scanner captures live sample
   → Hardware Bridge receives scan request
   → Scanner captures fingerprint

2. Generate live encoding
   → Use SAME model_version as stored templates
   → If model_version mismatch → Error: "System upgrade required"

3. Search for matches
   → Query BiometricIdentity table:
     WHERE biometric_type = 'fingerprint'
       AND is_active = true
       AND model_version = 'secugen_sdk_2.1'
   
   → Compare live encoding with stored encodings
   → Calculate similarity score (cosine similarity / Euclidean distance)

4. Match evaluation
   → If similarity >= 0.85 (threshold) → Match found
   → If multiple matches >= 0.85 → Conflict (rare)
   → If no match >= 0.85 → Authentication failed

5. Person identification
   → Single match → person_id identified
   → Multiple matches → Show disambiguation UI:
     "Multiple matches found. Please enter PIN:"
     [Ahmed Khan - Student]
     [Ahmed Ali - Teacher]
   
6. Role resolution
   → Load active UserRoleBindings for person_id + current_campus_id
   → Select appropriate role (if multiple, show picker)

7. Action performed
   → Mark attendance
   → Grant gate access
   → Log event in audit log
```

**Threshold Configuration:**

```python
BIOMETRIC_MATCH_THRESHOLDS = {
    'fingerprint': {
        'accept': 0.85,      # Minimum to accept
        'confident': 0.95,   # High confidence, no secondary check
        'reject': 0.60       # Below this, don't even show as option
    },
    'face': {
        'accept': 0.75,      # Faces are less precise
        'confident': 0.90,
        'reject': 0.50
    }
}
```

---

### 6.4 Model Version Management

**Critical Rule:** NEVER compare encodings from different model versions

**Why:**
* Upgrading DeepFace 0.0.75 → 0.0.79 changes encoding algorithm
* Old encodings become incompatible
* False rejections if compared across versions

**Upgrade Procedure:**

```
1. Schedule re-enrollment period
   → Notify all users: "Biometric system upgrade. Please re-register."

2. Mark old encodings inactive
   → UPDATE BiometricIdentity 
     SET is_active = false, 
         deactivated_reason = 'Model version upgrade to v0.0.79'
     WHERE model_version = 'deepface_0.0.75'

3. Mass re-enrollment
   → Set up enrollment stations
   → Process all users over 2-3 weeks
   → Old encodings remain for audit (not deleted)

4. Dual-version support (transition period)
   → System accepts BOTH old and new encodings
   → Gradual phase-out of old version
   → After 95% re-enrollment → Disable old version
```

---

### 6.5 Failure Modes & Fallbacks

**Scenario 1: Scanner Offline**

```
Attendance UI shows:
  ⚠ Biometric scanner offline
  [Switch to Manual Entry]
  
Admin can:
  → Manually mark attendance
  → Event logged as "manual_entry_due_to_device_failure"
```

**Scenario 2: Low Quality Scan**

```
After 3 failed scans:
  → "Unable to read fingerprint. Try different finger or use PIN."
  → Fallback to PIN entry
  → Event logged for investigation (damaged finger? scanner issue?)
```

**Scenario 3: Multiple Matches**

```
UI shows disambiguation:
  "Multiple possible matches. Select:"
  [ ] Ahmed Khan (Student, ID: 12345)
  [ ] Ahmed Ali (Teacher, ID: 67890)
  
After selection:
  → Require PIN verification
  → Log as "biometric_ambiguous_match"
```

**Scenario 4: Camera Offline (Face Recognition)**

```
Face recognition attendance:
  → Camera feed not available
  → Fallback to fingerprint
  → If fingerprint also unavailable → Manual entry
```

---

## 7. Revocation & Lifecycle Management

### 7.1 Role Removal

**Procedure:**

```python
def revoke_role_binding(binding_id, revoked_by_person_id, reason):
    """
    Revokes a role binding (does NOT delete)
    """
    binding = UserRoleBinding.objects.get(id=binding_id)
    
    # Set end date to today (if not already set)
    if not binding.valid_until:
        binding.valid_until = timezone.now().date()
    
    # Deactivate
    binding.is_active = False
    binding.deactivated_at = timezone.now()
    binding.deactivated_by_id = revoked_by_person_id
    binding.notes = f"{binding.notes or ''}\nRevoked: {reason}"
    binding.save()
    
    # Log event
    AuditLog.objects.create(
        person_id=revoked_by_person_id,
        action='revoke_role_binding',
        target_type='UserRoleBinding',
        target_id=binding_id,
        metadata={'reason': reason}
    )
```

**UI Flow:**

```
Admin → User Management → Ahmed Khan → Roles
  
[x] Teacher @ Morning Campus (Class 10-A)
    Valid: Jan 1 - Jun 30, 2025
    [Revoke] [Extend]

On [Revoke]:
  Modal: "Revoke this role?"
  Reason: [___________]
  Effective: [Today ▼] [Immediately ▼] [Custom Date]
  [Confirm]
```

---

### 7.2 UserAccount Locking (Temporary Suspension)

**Does NOT affect Person:**

```python
# Lock user account (e.g., security incident)
user_account = UserAccount.objects.get(username='ahmed')
user_account.is_locked = True
user_account.lockout_until = timezone.now() + timedelta(days=7)
user_account.save()

# Person's other accounts (if any) remain active
# Person's role bindings remain valid
# Person can still appear in reports, student lists, etc.
```

**Use cases:**
* Suspicious login activity
* Policy violation
* Password reset cooling period
* Temporary administrative hold

---

### 7.3 Person Deactivation (Leaving Institution)

**Cascades to all bindings:**

```python
def deactivate_person(person_id, deactivated_by_person_id, reason):
    """
    Deactivates person and all associated access
    """
    person = Person.objects.get(id=person_id)
    
    # Deactivate person
    person.is_active = False
    person.save()
    
    # Deactivate all role bindings
    bindings = UserRoleBinding.objects.filter(
        person_id=person_id,
        is_active=True
    )
    
    for binding in bindings:
        binding.is_active = False
        binding.deactivated_at = timezone.now()
        binding.deactivated_by_id = deactivated_by_person_id
        binding.notes = f"{binding.notes or ''}\nPerson deactivated: {reason}"
        binding.save()
    
    # Deactivate biometric identities
    BiometricIdentity.objects.filter(
        person_id=person_id,
        is_active=True
    ).update(
        is_active=False,
        deactivated_at=timezone.now(),
        deactivated_reason=reason
    )
    
    # Lock all user accounts
    UserAccount.objects.filter(person_id=person_id).update(is_locked=True)
    
    # Historical data remains intact
    # Student records, grades, attendance remain visible
```

**Use cases:**
* Student graduation
* Teacher resignation
* Expulsion / termination
* Death (handled sensitively)

---

### 7.4 Person Reactivation (Returning User)

```python
def reactivate_person(person_id, reactivated_by_person_id):
    """
    Reactivates person (bindings must be added separately)
    """
    person = Person.objects.get(id=person_id)
    person.is_active = True
    person.save()
    
    # Unlock primary user account
    UserAccount.objects.filter(
        person_id=person_id,
        is_locked=True
    ).first().update(is_locked=False)
    
    # NOTE: Role bindings are NOT auto-reactivated
    # Admin must create new bindings with new dates
    
    # Biometrics may need re-enrollment if model version changed
```

**Use cases:**
* Alumni returning as teacher
* Temporary leave ending
* Rehire after resignation

---

## 8. Audit & Traceability

### 8.1 Audit Log Schema

**Purpose:** Immutable record of all authorization-related events

**Table Structure:**

```python
AuditLog:
  id: UUID (primary key)
  person_id: UUID (who performed the action)
  user_account_id: bigint (which login session)
  campus_id: int (where)
  role_id: int (using which role, nullable)
  binding_id: bigint (which specific binding, nullable)
  permission: string (which permission was exercised)
  action: string (specific action performed)
  target_type: string (what was accessed: Student, Fee, Exam)
  target_id: bigint (specific record ID)
  ip_address: string
  user_agent: string
  timestamp: timestamp (immutable)
  result: enum ('success', 'denied', 'error')
  error_message: text (if result='error' or 'denied')
  metadata: json (additional context)
```

**Examples:**

```python
# Successful action
{
  person_id: UUID('123...'),
  user_account_id: 42,
  campus_id: 1,
  role_id: TEACHER,
  binding_id: 100,
  permission: 'academic.mark_attendance',
  action: 'mark_present',
  target_type: 'Student',
  target_id: 5678,
  ip_address: '192.168.1.50',
  user_agent: 'Mozilla/5.0...',
  timestamp: '2025-02-10T09:15:00Z',
  result: 'success',
  metadata: {
    'class_id': 15,
    'subject_id': 3,
    'date': '2025-02-10'
  }
}

# Denied action
{
  person_id: UUID('456...'),
  action: 'view_student_grades',
  permission: 'academic.view_grades',
  result: 'denied',
  error_message: 'Missing permission: academic.view_grades',
  metadata: {
    'attempted_student_id': 999,
    'active_role': 'parent'  # Parents can only see their own child's grades
  }
}
```

---

### 8.2 Audit Requirements

**Every authorization decision MUST be traceable:**

* Who accessed
* Which role they used
* Which campus context
* Which permission was checked
* What was the result (allowed/denied)
* When it occurred
* From where (IP address)

**Retention Policy:**

* Audit logs kept for **7 years** minimum (compliance requirement)
* Stored in append-only table (immutable)
* Daily backups to separate storage (off-site)
* Monthly archival to cold storage (cost optimization)

**Query Performance:**

* Indexed on: person_id, campus_id, timestamp, action
* Partitioned by month (for large installations)
* Archived logs moved to separate table after 1 year

---

### 8.3 Sensitive Actions (Enhanced Logging)

**Actions requiring extra audit detail:**

* `kernel.manage_users` (creating/deleting users)
* `kernel.manage_roles` (changing role permissions)
* `kernel.view_audit_logs` (viewing audit logs)
* `finance.bypass_approval` (overriding payment approvals)
* `academic.modify_grades` (changing submitted grades)
* `kernel.impersonate_user` (admin viewing as another user)

**Enhanced logging includes:**

```python
metadata: {
  'justification': 'Requested by Principal for investigation',
  'approval_id': 'APR_12345',  # If action required approval
  'before_value': {...},        # State before change
  'after_value': {...},         # State after change
  'witnesses': [person_id1, person_id2]  # If action witnessed
}
```

---

## 9. Module Interaction Rules

### 9.1 How Modules Consume Identity

**Modules MUST:**

* Query identity via Kernel services only
* Never import `kernel.models.Person` directly (use services)
* Never assign roles directly (use Kernel's RoleBindingService)
* Never bypass campus filtering
* Always pass campus context explicitly to background tasks

**Modules MUST NOT:**

* Create their own permission systems
* Store role information in module-specific tables
* Cache user permissions (they may change mid-session)
* Make assumptions about role names or IDs

---

### 9.2 Kernel Services for Modules

**Modules interact via these Kernel services:**

```python
# kernel/services/identity_service.py

class IdentityService:
    @staticmethod
    def get_person_by_id(person_id: UUID) -> Person:
        """Retrieve person by ID"""
        
    @staticmethod
    def get_active_roles(person_id: UUID, campus_id: int) -> List[Role]:
        """Get all active roles for person in campus"""
        
    @staticmethod
    def has_permission(person_id: UUID, campus_id: int, 
                       permission_code: str) -> bool:
        """Check if person has specific permission"""
        
    @staticmethod
    def can_access_entity(person_id: UUID, campus_id: int,
                         entity_type: str, entity_id: int) -> bool:
        """Check if person can access specific entity"""
        
    @staticmethod
    def get_accessible_entities(person_id: UUID, campus_id: int,
                                entity_type: str) -> List[int]:
        """Get all entity IDs person can access"""
        # Example: Get all class IDs Ahmed can teach
        # Returns: [15, 20] (Class 10-A, Class 10-B)
```

**Module Usage Example:**

```python
# modules/academic/services.py

from kernel.services import IdentityService

class AttendanceService:
    def mark_attendance(self, student_id, person_id, campus_id):
        # Check permission via Kernel
        if not IdentityService.has_permission(
            person_id, campus_id, 'academic.mark_attendance'
        ):
            raise PermissionDenied()
        
        # Check if teacher can access this student's class
        student = Student.objects.get(id=student_id)
        
        if not IdentityService.can_access_entity(
            person_id, campus_id, 'class', student.class_id
        ):
            raise PermissionDenied("You don't have access to this class")
        
        # Mark attendance...
```

---

## 10. AI-Agent Safety Rules

### 10.1 Constitutional Constraints

AI agents implementing this system **MUST**:

1. **Treat this document as final authority**
   * Never simplify identity models
   * Never assume "we can add this later"
   * Never compromise on separation of concerns

2. **Never collapse Person/User/Role concepts**
   * ❌ Don't create a single "User" table with role column
   * ✅ Keep Person, UserAccount, UserRoleBinding separate

3. **Always pass campus context explicitly**
   * ❌ Don't rely on middleware in service layer
   * ✅ Every service method receives `campus_id` parameter

4. **Never bypass campus filtering**
   * ❌ Don't use `.unfiltered_objects` in module code
   * ✅ Use `.objects` (auto-filtered) or service layer

5. **Validate before implementing**
   * Before generating code, confirm understanding
   * Ask questions if requirements are ambiguous
   * Flag violations of this constitution

---

### 10.2 Code Generation Rules

**When generating identity-related code:**

1. **Check this document first** before writing any model/service
2. **Use exact field names** from schema definitions
3. **Include all indexes** specified (performance critical)
4. **Add validation logic** from rules sections
5. **Generate tests** for authorization flows
6. **Document exceptions** to standard patterns (with justification)

**Forbidden shortcuts:**

* ❌ Storing role as string field in User model
* ❌ Hardcoding campus_id in queries
* ❌ Checking permissions in views (must be in service layer)
* ❌ Using session state in background tasks
* ❌ Mixing authentication and authorization logic

---

### 10.3 Verification Checklist

Before considering any identity feature "complete", verify:

- [ ] Person/UserAccount/Role/Binding models follow exact schema
- [ ] Campus context is passed explicitly to all services
- [ ] Authorization checks happen in service layer (not views)
- [ ] Temporal validity (valid_from/valid_until) is enforced
- [ ] Entity scoping rules are implemented correctly
- [ ] Audit logging captures all required fields
- [ ] Biometric data is encrypted
- [ ] Tests cover: multiple roles, campus switching, temporal overlaps
- [ ] Documentation explains WHY (not just WHAT)
- [ ] No violations of this constitution

---

## 11. Implementation Phases

### Phase 1: Core Tables (Week 1)

**Tasks:**
* Create Person model
* Create UserAccount model (integrate with Django auth)
* Create Role model (seed predefined roles)
* Create Permission model
* Create RolePermissionMap
* Create UserRoleBinding model
* Add database indexes
* Write model-level validation

**Deliverables:**
* Migrations for all tables
* Admin interface for manual testing
* Sample data (2 persons, 5 roles, 20 permissions)

---

### Phase 2: Services & Authorization (Week 2)

**Tasks:**
* Implement IdentityService
* Implement AuthorizationService
* Implement RoleBindingService (create/revoke bindings)
* Add temporal validation (valid_from/valid_until)
* Add entity scope validation
* Write unit tests for all services

**Deliverables:**
* `kernel/services/identity_service.py`
* `kernel/services/authorization_service.py`
* `kernel/services/role_binding_service.py`
* Test coverage > 90%

---

### Phase 3: Middleware & Context (Week 2)

**Tasks:**
* Implement CampusContextMiddleware
* Build context picker UI
* Build context switching UI (navbar dropdown)
* Implement thread-local campus storage
* Test campus isolation with 2+ campuses

**Deliverables:**
* `kernel/middleware/campus_context.py`
* `kernel/templates/select_context.html`
* Integration tests (context switching, permission checks)

---

### Phase 4: Audit Logging (Week 3)

**Tasks:**
* Create AuditLog model
* Implement audit logging service
* Add audit decorators for sensitive actions
* Build audit log viewer UI (admin only)
* Test log retention and query performance

**Deliverables:**
* `kernel/models/audit.py`
* `kernel/services/audit_service.py`
* `kernel/views/audit_logs.py`
* Performance tests (1M+ log entries)

---

### Phase 5: Biometric Integration (Week 5)

**Tasks:**
* Create BiometricIdentity model
* Build enrollment flow (UI + backend)
* Build authentication flow (scanner integration)
* Implement matching algorithm
* Handle failure modes (scanner offline, poor quality)
* Test with real hardware

**Deliverables:**
* `kernel/models/biometric.py`
* `kernel/services/biometric_service.py`
* Hardware bridge desktop app (Electron/Python)
* Integration tests with mock scanner

---

## 12. Security Considerations

### 12.1 Password Security

* PBKDF2 with 260,000 iterations (Django default)
* Salted hashes (per-user salt)
* Password history (prevent reuse of last 5 passwords)
* Complexity requirements (8+ chars, upper/lower/digit)
* Breach detection (check against haveibeenpwned API)

### 12.2 Session Security

* HTTP-only cookies (prevent XSS)
* Secure flag (HTTPS only)
* SameSite=Strict (CSRF protection)
* Session timeout: 30 minutes idle, 8 hours absolute
* Re-authentication for sensitive actions

### 12.3 Biometric Security

* Encryption at rest (AES-256)
* Encryption in transit (TLS 1.3)
* Templates never leave server unencrypted
* Access logs for biometric enrollment/viewing
* Hardware bridge authentication (device certificates)

### 12.4 Campus Isolation

* Row-level security (campus_id filter)
* No cross-campus queries in module code
* URL manipulation prevention
* Super-admin actions logged and monitored
* Quarterly penetration testing

---

## 13. Performance Targets

**Authorization check:** < 50ms (P95)
* Cached role permissions (5-minute TTL)
* Database indexes on critical fields
* Avoid N+1 queries (select_related, prefetch_related)

**Context switching:** < 200ms (P95)
* Session update only (no database writes)
* Cached binding lookups

**Biometric matching:** < 2 seconds (P95)
* 1:N search optimized with indexing
* Parallel matching (if 1000+ templates)
* Early rejection (quality score filter)

---

## 14. Compliance & Legal

### 14.1 Data Protection

* GDPR-compliant (if applicable)
* Right to erasure (anonymize, don't delete)
* Data portability (export person data)
* Consent tracking (biometric enrollment)

### 14.2 Audit Requirements

* SOC 2 Type II compatible
* 7-year retention (financial records)
* Immutable logs (append-only)
* Log integrity verification (checksums)

---

## Appendix A: Database Schema Diagram

```
Person (1) ──┬─< (M) UserAccount
             │
             ├─< (M) UserRoleBinding >── (1) Role ──< (M) RolePermissionMap >── (1) Permission
             │                    │
             │                    └─> (1) Campus
             │                    └─> (0..1) Entity (class/dept/hostel)
             │
             └─< (M) BiometricIdentity

AuditLog (logs all identity operations)
```

---

## Appendix B: Glossary

**Person:** Real human being (immutable identity)  
**UserAccount:** Login credentials (mutable, can have multiple)  
**Role:** Named responsibility (teacher, admin, student)  
**Permission:** Atomic action (view_student, mark_attendance)  
**Binding:** Link between person + role + campus + time  
**Campus Context:** Which campus a user is currently working in  
**Entity Scope:** Specific class/hostel/dept a role applies to  
**Temporal Validity:** Start/end dates for role bindings  
**Biometric Template:** Encoded fingerprint/face data  
**Model Version:** Version of biometric encoding algorithm  

---

**Status:** Universal Identity Model v2.0 — FINAL  
**Approved For:** AI Agent Implementation  
**Next Review:** After Phase 5 completion  
**Document Owner:** Nadeem (System Architect)

---

## Change Log

**v2.0 (2025-02-12):**
* Added context selection & switching flows (Section 3.3)
* Added entity scope resolution rules (Section 4.2)
* Added biometric authentication flow (Section 6.2-6.5)
* Added binding overlap rules (Section 2.6.1)
* Added audit log schema (Section 8.1)
* Added implementation phases (Section 11)
* Added security considerations (Section 12)
* Added performance targets (Section 13)

**v1.0 (2025-02-10):**
* Initial draft from architectural discussions
* Core models defined
* Authorization algorithm specified
* Campus context strategy defined
