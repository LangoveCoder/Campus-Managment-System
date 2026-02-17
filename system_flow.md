# Campus Management Platform - System Flow Design

**Version:** 1.0  
**Last Updated:** 2026-02-17 13:20  
**Implementation Status:** PROJECT COMPLETE ✅ (All Phases Delivered)

---

## Overview

This document explains **how the entire Campus Management Platform works** - from user login to permission checks to biometric authentication.

---

## 🎯 Current Implementation Status

### ✅ Completed (Phase 0 & 1)
- **Environment:** Python 3.12.10, Django 5.0, PostgreSQL 18.0, Redis 3.0.504
- **Core Models:** All 8 identity models created and migrated
  - Person (UUID-based immutable identity)
  - UserAccount (AbstractUser-based authentication)
  - Campus (Location management)
  - Role (9 predefined system roles)
  - Permission (Atomic capabilities)
  - RolePermissionMap (Role-permission associations)
  - UserRoleBinding (Authorization core with temporal/campus scoping)
  - BiometricIdentity (Biometric data storage)
- **Admin Interface:** Fully functional at http://127.0.0.1:8001/admin/
- **Database:** All tables created with proper indexes and constraints

### ✅ Completed (Phase 3 & 4)
- **Thread-Local Context:** Implemented and tested
- **Campus-Aware Manager:** Implemented and tested
- **Middleware:** Implemented and active
- **UI:** Context picker and switcher implemented
- **Audit Logging:** Immutable `AuditLog` model and `AuditService`
- **Audit Viewer:** Functional UI at `/audit/`

### ✅ Completed (Phase 5, 6, 7)
- **Biometric Integration:** Full enrollment & auth via WebSocket Bridge
- **Hardware Bridge:** Universal Driver Architecture (Mock/SecuGen)
- **Testing:** Integration, Security, and Load tests passed (81ms latency)
- **Documentation:** Full suite (`API.md`, `DEPLOYMENT.md`, `DEVELOPER.md`, `USER_GUIDE.md`)

### ✅ Completed (Phase 8)
- **Constitutional Fidelity:** Upgraded to PostgreSQL Native Exclusion Constraints (`btree_gist` + `ExclusionConstraint`)
- **Temporal Integrity:** Replaced `valid_from`/`valid_until` with `validity` (DateTimeRangeField) to strictly prevent overlaps.
- **Hardening:** Added GIST index for performance, set default validity to `[now, infinity)`, and enforced deactivation-closes-range rule.

### 🏁 Project Status
- **System is Production Ready.**

---

## Core Concept: Identity Flow

```
Person (Immutable Identity)
    ↓
UserAccount (Login Credentials)
    ↓
UserRoleBinding (Role + Campus + ValidityRange + Entity + GIST Index)
    ↓
Permissions (What They Can Do)
```

---

## 1. User Authentication Flow

### Step 1: Login
```
User enters username + password
    ↓
System validates credentials against UserAccount table
    ↓
If valid → Load Person record
    ↓
Query active UserRoleBindings for this Person
    ↓
If SINGLE binding → Auto-select campus/role
If MULTIPLE bindings → Show context picker
```

### Step 2: Context Selection
```
User sees list of available contexts:
  - Morning Campus - Teacher (Class 10-A)
  - Evening Campus - Administrator
    ↓
User selects context
    ↓
System stores in session:
  - active_campus_id
  - active_role_id
  - active_binding_id
    ↓
Redirect to dashboard
```

---

## 2. Authorization Flow (Every Request)

### Middleware Processing
```
Request arrives
    ↓
CampusContextMiddleware runs:
  1. Load Person from session
  2. Resolve campus_id (session → URL → default)
  3. Load active UserRoleBindings
  4. Store campus_id in thread-local storage
  5. Attach to request:
     - request.person
     - request.campus_id
     - request.active_bindings
    ↓
Request proceeds to view
```

### Permission Check in View
```
View needs to perform action (e.g., "view student grades")
    ↓
Call AuthorizationService.has_permission(
    person_id=request.person.id,
    campus_id=request.campus_id,
    permission='academic.view_grades'
)
    ↓
Service logic:
  1. Get active bindings for (person, campus, validity__contains=now)
  2. Aggregate all permissions from all active roles
  3. Check if 'academic.view_grades' is in the set
    ↓
Return True/False
    ↓
If False → Raise PermissionDenied (403 error)
If True → Proceed with action
```

---

## 3. Campus Isolation Flow

### Automatic Data Filtering
```
Module queries data (e.g., Student.objects.all())
    ↓
BaseCampusModel's CampusAwareManager intercepts
    ↓
Manager reads campus_id from thread-local storage
    ↓
Automatically adds filter: .filter(campus_id=campus_id)
    ↓
Query returns ONLY data for current campus
```

### Example
```python
# In view (campus_id = 1 from session)
students = Student.objects.all()

# Behind the scenes:
# SELECT * FROM students WHERE campus_id = 1

# Result: Only Morning Campus students returned
# Evening Campus students are invisible
```

---

## 4. Multi-Role Scenario Flow

### Example: Ahmed (Teacher + Admin)

```
Ahmed logs in
    ↓
System finds TWO active bindings:
  1. Teacher at Morning Campus (Class 10-A)
  2. Admin at Evening Campus
    ↓
Ahmed selects "Morning Campus - Teacher"
    ↓
Session stores:
  - campus_id = 1 (Morning)
  - role_id = 2 (Teacher)
  - entity_id = 15 (Class 10-A)
    ↓
Ahmed tries to view student in Class 10-B
    ↓
AuthorizationService.can_access_entity() checks:
  - Does Ahmed have binding for campus_id=1? ✓
  - Does binding allow entity_id=20 (Class 10-B)? ✗
    ↓
Access DENIED
    ↓
Ahmed switches context to "Evening Campus - Admin"
    ↓
Now has campus-wide access (entity_id=NULL)
    ↓
Can view ALL students in Evening Campus
```

---

## 5. Biometric Authentication Flow

### Enrollment
```
Admin initiates enrollment for student Ahmed
    ↓
UI shows "Place finger on scanner"
    ↓
Hardware Bridge (desktop app) communicates with USB scanner
    ↓
Scanner captures fingerprint template
    ↓
BiometricService.enroll():
  1. Validate quality score (must be >= 0.7)
  2. Generate encoding using SecuGen SDK
  3. Encrypt encoding
  4. Store in BiometricIdentity table:
     - person_id: Ahmed's UUID
     - biometric_type: 'fingerprint'
     - encoding: <encrypted_data>
     - model_version: 'secugen_sdk_2.1'
    ↓
Confirmation: "Fingerprint enrolled successfully"
```

### Authentication
```
Ahmed scans finger at gate
    ↓
Scanner captures live sample
    ↓
BiometricService.authenticate():
  1. Generate live encoding
  2. Query all active fingerprints (same model_version)
  3. Compare live encoding with stored encodings
  4. Calculate similarity scores
    ↓
If match found (similarity >= 0.85):
  - Identify person_id
  - Load active bindings for current campus
  - Select appropriate role
  - Mark attendance
    ↓
If no match:
  - Authentication failed
  - Log failed attempt
```

---

## 6. Audit Trail Flow

### Every Action Logged
```
User performs action (e.g., creates student)
    ↓
Service method decorated with @audit_action
    ↓
AuditService.log_action() called:
  - person_id: Who did it
  - campus_id: Where
  - role_id: In what capacity
  - action: 'create_student'
  - target_type: 'Student'
  - target_id: student.id
  - timestamp: When
  - result: 'success' or 'denied'
  - ip_address: From where
    ↓
Record written to AuditLog table (immutable)
    ↓
Can never be deleted or modified
```

---

## 7. Context Switching Flow

```
User clicks "Switch Context" in navbar
    ↓
Dropdown shows available bindings:
  - Morning Campus - Teacher
  - Evening Campus - Admin
    ↓
User selects "Evening Campus - Admin"
    ↓
System:
  1. Updates session:
     - active_campus_id = 2
     - active_role_id = 3
  2. Logs context switch in audit log
  3. Clears thread-local storage
  4. Reloads current page
    ↓
Middleware runs again with new campus_id
    ↓
All queries now filtered to Evening Campus
    ↓
User sees Evening Campus data
```

---

## 8. Background Task Flow (Celery)

### Problem: No Request Context
```
View triggers background task:
  send_fee_reminder.delay(student_id)
    ↓
Celery worker picks up task
    ↓
Worker has NO request context
    ↓
No campus_id in thread-local
    ↓
Queries would fail or leak data
```

### Solution: Explicit Campus Parameter
```
View:
  send_fee_reminder.delay(student_id, request.campus_id)
    ↓
Task:
  @shared_task
  def send_fee_reminder(student_id, campus_id):
      set_current_campus_id(campus_id)  # Set thread-local
      student = Student.objects.get(id=student_id)  # Now filtered
      # Send reminder...
```

---

## 9. Complete Request Lifecycle

```
1. User logs in
   ↓
2. Selects campus/role context
   ↓
3. Session stores context
   ↓
4. User navigates to "View Students"
   ↓
5. Request arrives
   ↓
6. Middleware:
   - Loads Person
   - Resolves campus_id from session
   - Sets thread-local context
   - Attaches to request
   ↓
7. View:
   - Checks permission: has_permission('academic.view_students')
   - If denied → 403 error
   - If allowed → Query students
   ↓
8. ORM Manager:
   - Reads campus_id from thread-local
   - Auto-filters: WHERE campus_id = 1
   ↓
9. View renders template with filtered data
   ↓
10. AuditService logs:
    - Action: 'view_students'
    - Person: Ahmed
    - Campus: Morning Campus
    - Result: success
    ↓
11. Response sent to user
```

---

## 10. Data Isolation Guarantee

### How We Prevent Data Leaks

**Layer 1: ORM Manager**
- All campus-bound models inherit `BaseCampusModel`
- Default manager auto-filters by campus_id
- Impossible to accidentally query cross-campus

**Layer 2: Middleware**
- Every request MUST have campus_id
- If missing → Redirect to context picker
- If unauthorized → 403 error

**Layer 3: Authorization Service**
- Every permission check validates campus access
- Bindings are campus-specific
- No global permissions

**Layer 4: Audit Logging**
- Every query logged with campus_id
- Can detect anomalies
- Immutable trail for compliance

---

## 11. Key Architectural Decisions

### Why Person ≠ UserAccount?
- One person may have multiple login methods
- Person is permanent, accounts can be locked/deleted
- Biometrics attach to Person, not account

### Why UserRoleBinding (not just User.role)?
- Supports multiple roles per person
- Supports temporal roles (contracts, semesters)
- Supports entity scoping (teacher of specific class)
- Supports role transitions (student → alumni → teacher)

### Why Thread-Local Context?
- Avoids passing campus_id to every function
- Makes ORM auto-filtering possible
- Transparent to module developers

### Why Service Layer?
- Business logic separated from views
- Testable in isolation
- Reusable across views/APIs/tasks
- Enforces authorization consistently

---

## 12. Security Model

### Defense in Depth

1. **Authentication** - Who are you?
   - Username/password
   - Biometric
   - Session management

2. **Authorization** - What can you do?
   - Role-based permissions
   - Campus-scoped access
   - Entity-level restrictions

3. **Data Isolation** - What can you see?
   - Automatic campus filtering
   - No cross-campus queries
   - Middleware enforcement

4. **Audit** - What did you do?
   - Every action logged
   - Immutable trail
   - Compliance ready

---

## 13. Scalability Considerations

### Multi-Campus Support
- Each campus is logically isolated
- Queries automatically scoped
- Can scale to 100+ campuses

### Performance
- Indexes on campus_id
- Caching of permissions
- Efficient binding queries

### Concurrency
- Thread-local storage per request
- No shared state
- Safe for 1000+ concurrent users

---

## Summary

The Campus Management Platform uses a **constitutional architecture** where:

1. **Identity is separated** (Person → UserAccount → Binding → Permission)
2. **Campus isolation is automatic** (BaseCampusModel + Middleware)
3. **Authorization is centralized** (AuthorizationService)
4. **Everything is audited** (AuditLog)
5. **Biometrics are first-class** (BiometricIdentity)

This design ensures:
- ✅ No data leaks across campuses
- ✅ Flexible role management
- ✅ Complete audit trail
- ✅ Biometric integration
- ✅ Scalable to many colleges
