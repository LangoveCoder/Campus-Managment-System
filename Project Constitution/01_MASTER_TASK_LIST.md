# Campus Management Platform - Master Task List

**Version:** 1.0  
**Last Updated:** 2025-02-12  
**Auto-Update Required:** AI Agent MUST update this file after completing each task  

---

## Instructions for AI Agent

1. **Before starting work:** Read this entire file
2. **After completing a task:** 
   * Update status from `[ ]` to `[✓]`
   * Add completion date
   * Add any notes about implementation decisions
   * Update the progress summary at the top
3. **If blocked:** Add `[BLOCKED]` tag and describe blocker
4. **If deviating from plan:** Add `[DEVIATION]` tag and justify
5. **Save this file after every change**

---

## Progress Summary (Auto-Updated)

**Overall Progress:** 0% (0 of 120 tasks completed)

**Phase Status:**
* ✗ Phase 0: Project Setup (0/8 tasks)
* ✗ Phase 1: Core Identity Tables (0/12 tasks)
* ✗ Phase 2: Authorization Services (0/15 tasks)
* ✗ Phase 3: Campus Context & Middleware (0/18 tasks)
* ✗ Phase 4: Audit Logging (0/10 tasks)
* ✗ Phase 5: Biometric Integration (0/20 tasks)
* ✗ Phase 6: Testing & Validation (0/15 tasks)
* ✗ Phase 7: Documentation & Handoff (0/8 tasks)

**Current Sprint:** Phase 0 - Project Setup  
**Estimated Completion:** TBD  
**Blockers:** None  

---

## PHASE 0: Project Setup & Foundation (Week 0)

**Goal:** Initialize Django project with proper structure following governance document

### Task 0.1: Environment Setup
- [ ] **0.1.1** Install Python 3.12+
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **0.1.2** Install PostgreSQL 16+
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **0.1.3** Install Redis (for Celery)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **0.1.4** Install Node.js (for docx generation, frontend tools)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 0.2: Django Project Initialization
- [ ] **0.2.1** Create Django 5.0 project: `campus_platform`
  - Status: Not Started
  - Command: `django-admin startproject config .`
  - Completion Date: 
  - Notes: 
  
- [ ] **0.2.2** Create folder structure per governance document:
  ```
  campus_platform/
  ├── kernel/
  ├── modules/
  ├── config/
  ├── requirements/
  └── manage.py
  ```
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **0.2.3** Setup requirements files:
  * requirements/base.txt (Django, psycopg2, celery, redis)
  * requirements/dev.txt (pytest, black, flake8)
  * requirements/prod.txt (gunicorn, whitenoise)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **0.2.4** Configure settings structure:
  * config/settings/base.py
  * config/settings/development.py
  * config/settings/production.py
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 0.3: Database Setup
- [ ] **0.3.1** Create PostgreSQL database: `campus_platform_dev`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **0.3.2** Configure Django database settings
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **0.3.3** Test database connection
  - Status: Not Started
  - Command: `python manage.py dbshell`
  - Completion Date: 
  - Notes: 

### Task 0.4: Initial Apps Creation
- [ ] **0.4.1** Create kernel app: `python manage.py startapp kernel`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **0.4.2** Create modules directory structure
  - Status: Not Started
  - Completion Date: 
  - Notes: 

---

## PHASE 1: Core Identity Tables (Week 1)

**Goal:** Implement all identity models per constitution v2

**Constitution Reference:** Section 2 (Core Identity Objects)

### Task 1.1: Person Model
- [ ] **1.1.1** Create `kernel/models/person.py`
  - Status: Not Started
  - Fields: id (UUID), full_name, date_of_birth, primary_email, primary_phone, created_at, is_active
  - Constitution: Section 2.1
  - Completion Date: 
  - Notes: 
  
- [ ] **1.1.2** Add indexes: primary_email, primary_phone
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.1.3** Add model validation (email/phone uniqueness)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.1.4** Create migration
  - Status: Not Started
  - Command: `python manage.py makemigrations kernel`
  - Completion Date: 
  - Notes: 

### Task 1.2: UserAccount Model
- [ ] **1.2.1** Create `kernel/models/user_account.py`
  - Status: Not Started
  - Inherits: AbstractBaseUser
  - Fields: id, person_id (FK), username, email, password_hash, last_login, is_locked, failed_login_attempts, lockout_until
  - Constitution: Section 2.2
  - Completion Date: 
  - Notes: 
  
- [ ] **1.2.2** Integrate with Django authentication system
  - Status: Not Started
  - Settings: AUTH_USER_MODEL = 'kernel.UserAccount'
  - Completion Date: 
  - Notes: 
  
- [ ] **1.2.3** Add password validation rules (8+ chars, complexity)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.2.4** Implement login attempt tracking
  - Status: Not Started
  - Logic: Lock after 5 failed attempts for 15 minutes
  - Completion Date: 
  - Notes: 

### Task 1.3: Campus Model
- [ ] **1.3.1** Create `kernel/models/campus.py`
  - Status: Not Started
  - Fields: id, name, campus_type (day/residential/hybrid), address, is_active
  - Completion Date: 
  - Notes: 
  
- [ ] **1.3.2** Create migration
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 1.4: Role Model
- [ ] **1.4.1** Create `kernel/models/role.py`
  - Status: Not Started
  - Fields: id, name (choices: student, teacher, admin, etc.), description, is_system_role
  - Constitution: Section 2.3
  - Completion Date: 
  - Notes: 
  
- [ ] **1.4.2** Seed predefined roles (data migration)
  - Status: Not Started
  - Roles: student, teacher, admin, principal, parent, warden, librarian, accountant, transport_manager
  - Completion Date: 
  - Notes: 

### Task 1.5: Permission Model
- [ ] **1.5.1** Create `kernel/models/permission.py`
  - Status: Not Started
  - Fields: id, code, name, module, description, is_dangerous
  - Constitution: Section 2.4
  - Completion Date: 
  - Notes: 
  
- [ ] **1.5.2** Add index on module field
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.5.3** Seed kernel permissions (data migration)
  - Status: Not Started
  - Permissions: kernel.manage_users, kernel.manage_roles, kernel.view_audit_logs
  - Completion Date: 
  - Notes: 

### Task 1.6: RolePermissionMap Model
- [ ] **1.6.1** Create `kernel/models/role_permission.py`
  - Status: Not Started
  - Fields: id, role_id (FK), permission_id (FK), granted_by (FK to Person)
  - Constitution: Section 2.5
  - Completion Date: 
  - Notes: 
  
- [ ] **1.6.2** Add unique constraint (role_id, permission_id)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.6.3** Seed default role-permission mappings (data migration)
  - Status: Not Started
  - Example: Teacher → [academic.view_student, academic.mark_attendance]
  - Completion Date: 
  - Notes: 

### Task 1.7: UserRoleBinding Model
- [ ] **1.7.1** Create `kernel/models/user_role_binding.py`
  - Status: Not Started
  - Fields: id, person_id, role_id, campus_id, entity_type, entity_id, valid_from, valid_until, is_active, created_at, created_by, deactivated_at, deactivated_by, notes
  - Constitution: Section 2.6
  - Completion Date: 
  - Notes: 
  
- [ ] **1.7.2** Add indexes: (person_id, campus_id, is_active), (valid_from, valid_until)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.7.3** Add unique constraint per overlap rules (Section 2.6.1)
  - Status: Not Started
  - Constraint: UNIQUE(person_id, role_id, campus_id, entity_id) WHERE is_active=true AND valid_until IS NULL
  - Completion Date: 
  - Notes: 
  
- [ ] **1.7.4** Implement is_currently_valid() method
  - Status: Not Started
  - Logic: Check is_active, valid_from <= today, valid_until >= today or NULL
  - Completion Date: 
  - Notes: 

### Task 1.8: BiometricIdentity Model
- [ ] **1.8.1** Create `kernel/models/biometric.py`
  - Status: Not Started
  - Fields: id (UUID), person_id, biometric_type, encoding (binary), model_version, quality_score, enrollment_device_id, enrolled_by, created_at, is_active, deactivated_at, deactivated_reason
  - Constitution: Section 6.1
  - Completion Date: 
  - Notes: 
  
- [ ] **1.8.2** Add index: (person_id, biometric_type, is_active)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.8.3** Implement encoding encryption (AES-256)
  - Status: Not Started
  - Library: cryptography (Fernet)
  - Completion Date: 
  - Notes: 

### Task 1.9: Run All Migrations
- [ ] **1.9.1** Generate migrations: `python manage.py makemigrations`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.9.2** Apply migrations: `python manage.py migrate`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.9.3** Verify tables in database
  - Status: Not Started
  - Command: `python manage.py dbshell` then `\dt kernel_*`
  - Completion Date: 
  - Notes: 

### Task 1.10: Admin Interface
- [ ] **1.10.1** Register all models in `kernel/admin.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.10.2** Create superuser for testing
  - Status: Not Started
  - Command: `python manage.py createsuperuser`
  - Completion Date: 
  - Notes: 
  
- [ ] **1.10.3** Test CRUD via admin interface
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 1.11: Sample Data
- [ ] **1.11.1** Create data migration with sample persons (2-3)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.11.2** Create sample user accounts
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **1.11.3** Create sample role bindings (multiple roles per person)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

---

## PHASE 2: Authorization Services (Week 2)

**Goal:** Implement business logic for authorization and role management

**Constitution Reference:** Section 4 (Authorization Algorithm)

### Task 2.1: Base Service Structure
- [ ] **2.1.1** Create `kernel/services/__init__.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **2.1.2** Create `kernel/services/base.py` with BaseService class
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 2.2: IdentityService
- [ ] **2.2.1** Create `kernel/services/identity_service.py`
  - Status: Not Started
  - Constitution: Section 9.2
  - Completion Date: 
  - Notes: 
  
- [ ] **2.2.2** Implement `get_person_by_id(person_id: UUID) -> Person`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **2.2.3** Implement `get_active_roles(person_id, campus_id) -> List[Role]`
  - Status: Not Started
  - Logic: Filter by is_active, valid_from <= today, valid_until >= today or NULL
  - Completion Date: 
  - Notes: 
  
- [ ] **2.2.4** Implement `get_accessible_entities(person_id, campus_id, entity_type) -> List[int]`
  - Status: Not Started
  - Logic: Aggregate all entity_ids from active bindings
  - Completion Date: 
  - Notes: 

### Task 2.3: AuthorizationService
- [ ] **2.3.1** Create `kernel/services/authorization_service.py`
  - Status: Not Started
  - Constitution: Section 4.1
  - Completion Date: 
  - Notes: 
  
- [ ] **2.3.2** Implement `get_active_bindings(person_id, campus_id) -> List[UserRoleBinding]`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **2.3.3** Implement `get_permissions(person_id, campus_id) -> set`
  - Status: Not Started
  - Logic: Aggregate all permissions from all active roles (additive)
  - Completion Date: 
  - Notes: 
  
- [ ] **2.3.4** Implement `has_permission(person_id, campus_id, permission_code) -> bool`
  - Status: Not Started
  - Constitution: Section 4.1 (canonical algorithm)
  - Completion Date: 
  - Notes: 
  
- [ ] **2.3.5** Implement `can_access_entity(person_id, campus_id, entity_type, entity_id) -> bool`
  - Status: Not Started
  - Constitution: Section 4.2 (entity scope rules)
  - Logic: NULL entity_id beats specific, multiple specifics are additive
  - Completion Date: 
  - Notes: 

### Task 2.4: RoleBindingService
- [ ] **2.4.1** Create `kernel/services/role_binding_service.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **2.4.2** Implement `create_binding(person_id, role_id, campus_id, entity_type, entity_id, valid_from, valid_until, created_by) -> UserRoleBinding`
  - Status: Not Started
  - Logic: Validate overlap rules (Section 2.6.1)
  - Completion Date: 
  - Notes: 
  
- [ ] **2.4.3** Implement overlap validation logic
  - Status: Not Started
  - Rules: Reject same (person, role, campus, entity) with overlapping dates
  - Completion Date: 
  - Notes: 
  
- [ ] **2.4.4** Implement `revoke_binding(binding_id, revoked_by, reason)`
  - Status: Not Started
  - Constitution: Section 7.1
  - Logic: Set is_active=false, valid_until=today, deactivated_at=now
  - Completion Date: 
  - Notes: 
  
- [ ] **2.4.5** Implement `extend_binding(binding_id, new_valid_until)`
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 2.5: PersonService
- [ ] **2.5.1** Create `kernel/services/person_service.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **2.5.2** Implement `create_person(full_name, email, phone, ...) -> Person`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **2.5.3** Implement `deactivate_person(person_id, deactivated_by, reason)`
  - Status: Not Started
  - Constitution: Section 7.3
  - Logic: Deactivate person, all bindings, biometrics, lock user accounts
  - Completion Date: 
  - Notes: 
  
- [ ] **2.5.4** Implement `reactivate_person(person_id, reactivated_by)`
  - Status: Not Started
  - Constitution: Section 7.4
  - Logic: Reactivate person, unlock primary account (bindings NOT auto-reactivated)
  - Completion Date: 
  - Notes: 

### Task 2.6: Unit Tests
- [ ] **2.6.1** Create `kernel/tests/test_identity_service.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **2.6.2** Create `kernel/tests/test_authorization_service.py`
  - Status: Not Started
  - Tests: Single role, multiple roles, temporal validity, entity scoping
  - Completion Date: 
  - Notes: 
  
- [ ] **2.6.3** Create `kernel/tests/test_role_binding_service.py`
  - Status: Not Started
  - Tests: Overlap validation, revocation, extension
  - Completion Date: 
  - Notes: 
  
- [ ] **2.6.4** Run tests: `pytest kernel/tests/`
  - Status: Not Started
  - Target: 100% service layer coverage
  - Completion Date: 
  - Notes: 

---

## PHASE 3: Campus Context & Middleware (Week 2-3)

**Goal:** Implement automatic campus context resolution and switching

**Constitution Reference:** Section 3 (Campus Context Resolution)

### Task 3.1: Thread-Local Context
- [ ] **3.1.1** Create `kernel/context.py` with thread-local storage
  - Status: Not Started
  - Code: `import threading; _thread_locals = threading.local()`
  - Completion Date: 
  - Notes: 
  
- [ ] **3.1.2** Implement `set_current_campus_id(campus_id)`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.1.3** Implement `get_current_campus_id() -> int`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.1.4** Implement `clear_campus_context()`
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 3.2: Campus-Aware Manager
- [ ] **3.2.1** Create `kernel/managers.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.2.2** Implement `CampusAwareManager(models.Manager)`
  - Status: Not Started
  - Logic: Override get_queryset() to filter by campus_id from thread-local
  - Completion Date: 
  - Notes: 
  
- [ ] **3.2.3** Test auto-filtering with sample queries
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 3.3: BaseCampusModel
- [ ] **3.3.1** Create `kernel/models/base.py`
  - Status: Not Started
  - Constitution: Section 5.1
  - Completion Date: 
  - Notes: 
  
- [ ] **3.3.2** Implement `BaseCampusModel(models.Model)`
  - Status: Not Started
  - Fields: campus (FK to Campus)
  - Managers: objects (CampusAwareManager), unfiltered_objects (default)
  - Meta: abstract = True
  - Completion Date: 
  - Notes: 
  
- [ ] **3.3.3** Add documentation for module developers
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 3.4: Campus Context Middleware
- [ ] **3.4.1** Create `kernel/middleware/campus_context.py`
  - Status: Not Started
  - Constitution: Section 3.2
  - Completion Date: 
  - Notes: 
  
- [ ] **3.4.2** Implement `CampusContextMiddleware`
  - Status: Not Started
  - Steps per Section 3.2:
    1. Resolve campus from URL/session/default
    2. Attach request.campus_id
    3. Attach request.person
    4. Attach request.active_bindings
    5. Store in thread-local
  - Completion Date: 
  - Notes: 
  
- [ ] **3.4.3** Handle missing campus (redirect to context picker)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.4.4** Handle unauthorized campus access (access denied page)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.4.5** Add middleware to settings.MIDDLEWARE
  - Status: Not Started
  - Position: After AuthenticationMiddleware
  - Completion Date: 
  - Notes: 

### Task 3.5: Context Picker UI
- [ ] **3.5.1** Create view `kernel/views/context_picker.py`
  - Status: Not Started
  - Constitution: Section 3.3.2
  - Completion Date: 
  - Notes: 
  
- [ ] **3.5.2** Create template `kernel/templates/select_context.html`
  - Status: Not Started
  - Display: List all active bindings (campus + role + entity if applicable)
  - Show: Validity dates, default indicator
  - Include: "Remember this choice" checkbox
  - Completion Date: 
  - Notes: 
  
- [ ] **3.5.3** Implement context selection logic
  - Status: Not Started
  - Action: Update session with selected campus_id, role_id, binding_id
  - Redirect: To dashboard or requested page
  - Completion Date: 
  - Notes: 
  
- [ ] **3.5.4** Add URL route: `/kernel/select-context`
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 3.6: Context Switching UI
- [ ] **3.6.1** Create view `kernel/views/switch_context.py`
  - Status: Not Started
  - Constitution: Section 3.3.3
  - Completion Date: 
  - Notes: 
  
- [ ] **3.6.2** Create partial template `kernel/templates/_context_switcher.html`
  - Status: Not Started
  - Display: Dropdown in navbar showing current context
  - Options: List all active bindings
  - Completion Date: 
  - Notes: 
  
- [ ] **3.6.3** Implement context switch logic
  - Status: Not Started
  - Action: Update session, log event, reload page
  - Rate limit: Max 10 switches per day (prevent abuse)
  - Completion Date: 
  - Notes: 
  
- [ ] **3.6.4** Add URL route: `/kernel/switch-context`
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 3.7: Dashboard (Landing Page)
- [ ] **3.7.1** Create view `kernel/views/dashboard.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.7.2** Create template `kernel/templates/dashboard.html`
  - Status: Not Started
  - Display: Current context, available modules, quick actions
  - Completion Date: 
  - Notes: 
  
- [ ] **3.7.3** Add URL route: `/` (root)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 3.8: Integration Tests
- [ ] **3.8.1** Create `kernel/tests/test_campus_context.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.8.2** Test: Campus resolution (URL > session > default)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.8.3** Test: Context picker with multiple bindings
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.8.4** Test: Context switching
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **3.8.5** Test: Auto-filtering with BaseCampusModel
  - Status: Not Started
  - Setup: 2 campuses, 10 students each
  - Verify: Only current campus students returned
  - Completion Date: 
  - Notes: 
  
- [ ] **3.8.6** Test: Unauthorized campus access (403)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

---

## PHASE 4: Audit Logging (Week 3)

**Goal:** Implement immutable audit trail for all identity operations

**Constitution Reference:** Section 8 (Audit & Traceability)

### Task 4.1: AuditLog Model
- [ ] **4.1.1** Create `kernel/models/audit.py`
  - Status: Not Started
  - Constitution: Section 8.1
  - Fields: id (UUID), person_id, user_account_id, campus_id, role_id, binding_id, permission, action, target_type, target_id, ip_address, user_agent, timestamp, result, error_message, metadata (JSON)
  - Completion Date: 
  - Notes: 
  
- [ ] **4.1.2** Add indexes: (person_id), (campus_id), (timestamp), (action)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **4.1.3** Add Meta: managed = False for append-only enforcement (optional)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **4.1.4** Create migration
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 4.2: AuditService
- [ ] **4.2.1** Create `kernel/services/audit_service.py`
  - Status: Not Started
  - Constitution: Section 8
  - Completion Date: 
  - Notes: 
  
- [ ] **4.2.2** Implement `log_action(person_id, action, target_type, target_id, result, **kwargs)`
  - Status: Not Started
  - Parameters: campus_id, role_id, permission, ip_address, user_agent, error_message, metadata
  - Completion Date: 
  - Notes: 
  
- [ ] **4.2.3** Implement `log_authorization_check(person_id, permission, result, campus_id)`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **4.2.4** Implement `log_context_switch(person_id, from_campus_id, to_campus_id, from_role_id, to_role_id)`
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 4.3: Audit Decorators
- [ ] **4.3.1** Create `kernel/decorators/audit.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **4.3.2** Implement `@audit_action(action, target_type)` decorator
  - Status: Not Started
  - Usage: Wrap service methods to auto-log
  - Example: `@audit_action('create_user', 'Person')`
  - Completion Date: 
  - Notes: 
  
- [ ] **4.3.3** Implement `@audit_permission(permission_code)` decorator
  - Status: Not Started
  - Usage: Log permission checks
  - Completion Date: 
  - Notes: 

### Task 4.4: Integrate Audit Logging
- [ ] **4.4.1** Add audit logging to AuthorizationService.has_permission()
  - Status: Not Started
  - Log: Every permission check (success/denied)
  - Completion Date: 
  - Notes: 
  
- [ ] **4.4.2** Add audit logging to RoleBindingService (create/revoke/extend)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **4.4.3** Add audit logging to PersonService (create/deactivate/reactivate)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **4.4.4** Add audit logging to context switching
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 4.5: Audit Log Viewer
- [ ] **4.5.1** Create view `kernel/views/audit_logs.py`
  - Status: Not Started
  - Permissions: kernel.view_audit_logs (admin only)
  - Completion Date: 
  - Notes: 
  
- [ ] **4.5.2** Create template `kernel/templates/audit_logs.html`
  - Status: Not Started
  - Features: Filters (person, campus, action, date range), pagination
  - Completion Date: 
  - Notes: 
  
- [ ] **4.5.3** Add URL route: `/kernel/audit-logs`
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 4.6: Performance Testing
- [ ] **4.6.1** Generate 1M sample audit log entries
  - Status: Not Started
  - Tool: Django management command
  - Completion Date: 
  - Notes: 
  
- [ ] **4.6.2** Test query performance (target: < 1 second for filtered queries)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **4.6.3** Optimize indexes if needed
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 4.7: Retention Policy Implementation
- [ ] **4.7.1** Create management command: `archive_old_audit_logs`
  - Status: Not Started
  - Logic: Move logs older than 1 year to archive table
  - Constitution: Section 8.2
  - Completion Date: 
  - Notes: 
  
- [ ] **4.7.2** Schedule as monthly cron job (document in deployment guide)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

---

## PHASE 5: Biometric Integration (Week 5)

**Goal:** Implement biometric enrollment and authentication flows

**Constitution Reference:** Section 6 (Hardware & Biometric Identity)

### Task 5.1: Biometric Service (Backend)
- [ ] **5.1.1** Create `kernel/services/biometric_service.py`
  - Status: Not Started
  - Constitution: Section 6
  - Completion Date: 
  - Notes: 
  
- [ ] **5.1.2** Implement `enroll_biometric(person_id, biometric_type, encoding, model_version, quality_score, device_id, enrolled_by)`
  - Status: Not Started
  - Constitution: Section 6.2
  - Completion Date: 
  - Notes: 
  
- [ ] **5.1.3** Implement quality validation (reject if quality_score < 0.7)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.1.4** Implement encoding encryption (AES-256 via Fernet)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.1.5** Implement `authenticate_biometric(live_encoding, biometric_type, campus_id) -> Person or None`
  - Status: Not Started
  - Constitution: Section 6.3
  - Logic:
    1. Query active BiometricIdentity for type + model_version
    2. Decrypt stored encodings
    3. Compare with live encoding (similarity score)
    4. Return person_id if match >= threshold (0.85)
  - Completion Date: 
  - Notes: 
  
- [ ] **5.1.6** Implement similarity calculation (cosine similarity or Euclidean distance)
  - Status: Not Started
  - Library: numpy or scikit-learn
  - Completion Date: 
  - Notes: 
  
- [ ] **5.1.7** Handle multiple matches (disambiguation logic)
  - Status: Not Started
  - Constitution: Section 6.5 (Scenario 3)
  - Completion Date: 
  - Notes: 

### Task 5.2: Device Registry
- [ ] **5.2.1** Create `kernel/models/device.py`
  - Status: Not Started
  - Fields: id, device_type (fingerprint_scanner, camera), model, campus_id, location, status (online/offline), last_heartbeat
  - Completion Date: 
  - Notes: 
  
- [ ] **5.2.2** Create migration
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.2.3** Implement device registration API endpoint
  - Status: Not Started
  - Endpoint: POST /api/devices/register
  - Completion Date: 
  - Notes: 
  
- [ ] **5.2.4** Implement heartbeat API endpoint
  - Status: Not Started
  - Endpoint: POST /api/devices/heartbeat
  - Logic: Update last_heartbeat timestamp
  - Completion Date: 
  - Notes: 
  
- [ ] **5.2.5** Create background task to mark devices offline (no heartbeat > 2 minutes)
  - Status: Not Started
  - Celery task scheduled every 1 minute
  - Completion Date: 
  - Notes: 

### Task 5.3: Biometric API Endpoints
- [ ] **5.3.1** Create `kernel/api/biometric.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.3.2** Implement POST `/api/biometric/enroll`
  - Status: Not Started
  - Request: {person_id, biometric_type, encoding, model_version, quality_score, device_id}
  - Response: {success, biometric_id}
  - Completion Date: 
  - Notes: 
  
- [ ] **5.3.3** Implement POST `/api/biometric/authenticate`
  - Status: Not Started
  - Request: {live_encoding, biometric_type, campus_id}
  - Response: {success, person_id, confidence_score} or {success: false, matches: [list if multiple]}
  - Completion Date: 
  - Notes: 
  
- [ ] **5.3.4** Implement POST `/api/biometric/verify` (1:1 match)
  - Status: Not Started
  - Request: {person_id, live_encoding}
  - Response: {match: true/false, confidence_score}
  - Completion Date: 
  - Notes: 

### Task 5.4: Enrollment UI
- [ ] **5.4.1** Create view `kernel/views/biometric_enrollment.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.4.2** Create template `kernel/templates/enroll_biometric.html`
  - Status: Not Started
  - Features: Person selector, biometric type selector, live scanner status, capture button, quality indicator
  - Completion Date: 
  - Notes: 
  
- [ ] **5.4.3** Add JavaScript for scanner communication
  - Status: Not Started
  - Protocol: WebSocket to local hardware bridge
  - Completion Date: 
  - Notes: 
  
- [ ] **5.4.4** Implement enrollment workflow (UI)
  - Status: Not Started
  - Flow per Section 6.2:
    1. Admin selects person
    2. Clicks "Capture Fingerprint"
    3. Scanner captures (via bridge)
    4. Quality check
    5. Store + confirm
  - Completion Date: 
  - Notes: 

### Task 5.5: Hardware Bridge (Desktop App)
- [ ] **5.5.1** Choose framework (Electron + Node.js or Python + PyQt)
  - Status: Not Started
  - Decision: 
  - Completion Date: 
  - Notes: 
  
- [ ] **5.5.2** Implement USB scanner driver integration (SecuGen SDK)
  - Status: Not Started
  - Platform: Windows (primary), Linux (optional)
  - Completion Date: 
  - Notes: 
  
- [ ] **5.5.3** Implement WebSocket server (local port 8765)
  - Status: Not Started
  - Library: ws (Node.js) or websockets (Python)
  - Completion Date: 
  - Notes: 
  
- [ ] **5.5.4** Implement capture command handler
  - Status: Not Started
  - Message: {action: 'capture_fingerprint', session_id: '...'}
  - Response: {success: true, encoding: '...', quality_score: 0.92}
  - Completion Date: 
  - Notes: 
  
- [ ] **5.5.5** Implement authentication with Django backend (device certificates)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.5.6** Build installer (Windows .exe, Linux .deb)
  - Status: Not Started
  - Tool: electron-builder or PyInstaller
  - Completion Date: 
  - Notes: 

### Task 5.6: Face Recognition (Optional - If Time Permits)
- [ ] **5.6.1** Install DeepFace library: `pip install deepface`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.6.2** Implement face encoding generation
  - Status: Not Started
  - Code: `from deepface import DeepFace; embedding = DeepFace.represent(img_path, model_name='Facenet512')`
  - Completion Date: 
  - Notes: 
  
- [ ] **5.6.3** Implement face matching
  - Status: Not Started
  - Code: `DeepFace.verify(img1, img2, model_name='Facenet512')`
  - Completion Date: 
  - Notes: 
  
- [ ] **5.6.4** Create camera capture UI (browser webcam access)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 5.7: Failure Mode Handling
- [ ] **5.7.1** Implement fallback to manual entry if scanner offline
  - Status: Not Started
  - Constitution: Section 6.5 (Scenario 1)
  - Completion Date: 
  - Notes: 
  
- [ ] **5.7.2** Implement retry logic for low quality scans (max 3 attempts)
  - Status: Not Started
  - Constitution: Section 6.5 (Scenario 2)
  - Completion Date: 
  - Notes: 
  
- [ ] **5.7.3** Implement disambiguation UI for multiple matches
  - Status: Not Started
  - Constitution: Section 6.5 (Scenario 3)
  - Completion Date: 
  - Notes: 

### Task 5.8: Model Version Management
- [ ] **5.8.1** Document model upgrade procedure
  - Status: Not Started
  - Constitution: Section 6.4
  - Completion Date: 
  - Notes: 
  
- [ ] **5.8.2** Create management command: `invalidate_old_biometrics`
  - Status: Not Started
  - Logic: Mark all encodings with old model_version as is_active=false
  - Completion Date: 
  - Notes: 
  
- [ ] **5.8.3** Create re-enrollment tracking system
  - Status: Not Started
  - Table: BiometricReenrollment (person_id, old_model_version, new_model_version, reenrolled_at)
  - Completion Date: 
  - Notes: 

### Task 5.9: Testing
- [ ] **5.9.1** Create `kernel/tests/test_biometric_service.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.9.2** Test: Enrollment with valid encoding (quality >= 0.7)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.9.3** Test: Enrollment rejection (quality < 0.7)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.9.4** Test: Authentication with exact match
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.9.5** Test: Authentication with no match
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.9.6** Test: Multiple matches (disambiguation)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.9.7** Test: Model version mismatch (should reject)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 5.10: Hardware Testing (Real Devices)
- [ ] **5.10.1** Test with SecuGen Hamster Plus scanner
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.10.2** Test enrollment with 10+ people
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **5.10.3** Test authentication accuracy (false accept rate, false reject rate)
  - Status: Not Started
  - Target: FAR < 0.1%, FRR < 1%
  - Completion Date: 
  - Notes: 

---

## PHASE 6: Testing & Validation (Week 6)

**Goal:** Comprehensive testing of entire identity system

### Task 6.1: Integration Testing
- [ ] **6.1.1** Create `kernel/tests/test_integration.py`
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **6.1.2** Test: Full user journey (create person → create account → assign role → login → context selection → permission check)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **6.1.3** Test: Multi-campus isolation
  - Status: Not Started
  - Setup: 2 campuses, 5 students each, 1 teacher with access to both
  - Verify: Teacher sees only current campus students
  - Completion Date: 
  - Notes: 
  
- [ ] **6.1.4** Test: Multi-role permission aggregation
  - Status: Not Started
  - Setup: Person with Teacher + Admin roles
  - Verify: Has union of both permission sets
  - Completion Date: 
  - Notes: 
  
- [ ] **6.1.5** Test: Temporal validity (role starts in future, role expired)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **6.1.6** Test: Entity scoping (teacher can access only assigned classes)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 6.2: Security Testing
- [ ] **6.2.1** Test: Cross-campus data leakage prevention
  - Status: Not Started
  - Attempt: Manually query different campus_id in URL
  - Expected: 403 Forbidden or redirect
  - Completion Date: 
  - Notes: 
  
- [ ] **6.2.2** Test: Unauthorized permission access
  - Status: Not Started
  - Attempt: Student role trying to access kernel.manage_users
  - Expected: PermissionDenied
  - Completion Date: 
  - Notes: 
  
- [ ] **6.2.3** Test: Session hijacking prevention (CSRF tokens)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **6.2.4** Test: SQL injection via permission checks
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 6.3: Performance Testing
- [ ] **6.3.1** Load test: 1000 concurrent users
  - Status: Not Started
  - Tool: locust or JMeter
  - Target: < 500ms response time (P95)
  - Completion Date: 
  - Notes: 
  
- [ ] **6.3.2** Load test: Permission checks (10,000 checks/second)
  - Status: Not Started
  - Target: < 50ms per check
  - Completion Date: 
  - Notes: 
  
- [ ] **6.3.3** Database query optimization
  - Status: Not Started
  - Tool: Django Debug Toolbar, EXPLAIN ANALYZE
  - Completion Date: 
  - Notes: 

### Task 6.4: Edge Case Testing
- [ ] **6.4.1** Test: Person with no active bindings (should redirect to "no access")
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **6.4.2** Test: Binding overlap edge cases (same role, different entities)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **6.4.3** Test: Deactivated person attempting login
  - Status: Not Started
  - Expected: Authentication succeeds but authorization fails
  - Completion Date: 
  - Notes: 
  
- [ ] **6.4.4** Test: Locked user account
  - Status: Not Started
  - Expected: Login rejected with appropriate message
  - Completion Date: 
  - Notes: 

### Task 6.5: Documentation Testing
- [ ] **6.5.1** Verify all constitution rules are implemented
  - Status: Not Started
  - Method: Manual checklist against constitution sections
  - Completion Date: 
  - Notes: 
  
- [ ] **6.5.2** Verify no deviations from constitution
  - Status: Not Started
  - Completion Date: 
  - Notes: 

---

## PHASE 7: Documentation & Handoff (Week 7)

**Goal:** Prepare complete documentation for next AI agent or developer

### Task 7.1: API Documentation
- [ ] **7.1.1** Generate API documentation using Sphinx or DRF's auto-docs
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **7.1.2** Document all service methods (parameters, return types, exceptions)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 7.2: Deployment Guide
- [ ] **7.2.1** Write `DEPLOYMENT.md`
  - Status: Not Started
  - Sections: Requirements, installation, database setup, configuration, migrations, initial data
  - Completion Date: 
  - Notes: 
  
- [ ] **7.2.2** Create Docker Compose configuration (optional but recommended)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 7.3: Developer Guide
- [ ] **7.3.1** Write `DEVELOPER_GUIDE.md`
  - Status: Not Started
  - Sections: Project structure, coding standards, testing, debugging
  - Completion Date: 
  - Notes: 
  
- [ ] **7.3.2** Create module template (for future module development)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 7.4: User Guide
- [ ] **7.4.1** Write `USER_GUIDE.md`
  - Status: Not Started
  - Sections: Login, context selection, context switching, role management
  - Completion Date: 
  - Notes: 
  
- [ ] **7.4.2** Create video walkthrough (optional)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

### Task 7.5: Handoff Preparation
- [ ] **7.5.1** Update this task list with final completion dates
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **7.5.2** Update flowchart with all completed tasks (green)
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **7.5.3** Create CHANGELOG.md with all implemented features
  - Status: Not Started
  - Completion Date: 
  - Notes: 
  
- [ ] **7.5.4** Prepare demo environment (staging server with sample data)
  - Status: Not Started
  - Completion Date: 
  - Notes: 

---

## BLOCKERS & RISKS

**Current Blockers:** None

**Risk Log:**
* None identified yet

**Decisions Log:**
* None yet

---

## NOTES FOR NEXT AI AGENT

**Critical Reminders:**
1. ALWAYS read constitution before implementing any identity feature
2. NEVER simplify Person/UserAccount/Role separation
3. NEVER bypass campus filtering in module code
4. ALWAYS pass campus_id explicitly to service methods
5. ALWAYS update this task list after completing tasks
6. Test campus isolation after EVERY new feature

**Helpful Commands:**
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest kernel/tests/ -v

# Run dev server
python manage.py runserver

# Django shell (for testing queries)
python manage.py shell

# Check for N+1 queries
python manage.py runserver --settings=config.settings.development
# Then use Django Debug Toolbar
```

**Common Pitfalls to Avoid:**
1. Using .unfiltered_objects in module code (only for super-admin views)
2. Forgetting to pass campus_id to Celery tasks
3. Hardcoding role IDs (use Role.STUDENT, Role.TEACHER constants)
4. Skipping temporal validation (valid_from, valid_until)
5. Not logging sensitive actions to audit log

---

## CHANGELOG

**2025-02-12:** Initial task list created
