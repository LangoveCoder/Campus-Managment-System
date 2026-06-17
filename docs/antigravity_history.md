# Antigravity IDE — Full Development Lineage

**Source:** Gemini Antigravity IDE (Conversation `0b480c1a-b160-4af1-a038-84cda2691487`)
**Consolidated:** 2026-06-17
**Purpose:** Preserve full project history for future agents (Claude Code, Gemini, etc.)

---

## Project Timeline

| Phase | Name | Date | Tasks |
|-------|------|------|-------|
| 0 | Environment Setup | 2026-02-12 | 12/12 |
| 1 | Core Identity Tables | 2026-02-12 | 22/22 |
| 2 | Authorization Services | 2026-02-12 | 15/15 |
| 3 | Campus Context & Middleware | 2026-02-12 | 18/18 |
| 4 | Audit Logging | 2026-02-12 | 10/10 |
| 5 | Biometric Integration | 2026-02-14 | 20/20 |
| 6 | Testing & Validation | 2026-02-14 | 15/15 |
| 7 | Documentation & Handoff | 2026-02-14 | 8/8 |
| 8 | Constitutional Fidelity (Temporal Upgrade) | 2026-02-14 | 5/5 |
| 8.3 | Constitutional Hardening | 2026-02-17 | — |
| 9 | Academic Core | 2026-02-18 | 20/20 |
| 10 | Admissions Module | 2026-02-19 | 15/15 |
| 11 | Attendance Module (Student Ledger) | 2026-02-19 | 15/15 |
| 12 | Workforce Attendance v1 | 2026-02-20 | 15/15 |
| — | Pre-Dashboard Surgical Repairs | 2026-02-20 | — |
| 13 | Dashboard API Layer | 2026-02-20 | — |
| 14 | JWT Authentication | 2026-02-20 | — |
| 15 | Integration Test Suite | 2026-02-20 | 36/36 |
| 16 | Dashboard UI | 2026-02-22 | — |
| 17 | Academic Seed Data | 2026-02-22 | — |
| 18 | Academics UI + Admissions Handoff + Workforce Staff | 2026-02–05 | — |
| 19 | Profiles Module | 2026-06-17 | 7/7 |

---

## Architecture Rules (Constitutional)

1. **Views call Service layer only** — no ORM in views
2. **Templates use context variables only** — no service or model calls in templates
3. **Every authenticated view**: `is_authenticated` → `current_campus_id` from session → `AuthorizationService.require_permission()` → service call
4. **`_get_person_id(request)` helper** — never `request.user.person_id` directly
5. **All `{% if %}` tags** use spaces around `==` (Django template syntax)
6. **Cross-module access via AuthorizationFacade** — no direct model imports across modules
7. **Permissions namespaced**: `module.action` format (e.g., `attendance.view_attendance`)
8. **Campus isolation**: BaseCampusModel + CampusAwareManager auto-filter by campus_id

---

## Critical Errors & Resolutions

### Python 3.14 → 3.12 Downgrade
- Python 3.14.0 incompatible with Django 5.0 (AttributeError in template rendering)
- Downgraded to Python 3.12.10 — always use `venv312`

### Virtual Environment Corruption
- `pyvenv.cfg` missing, pip/django modules vanished
- Recreated `venv312` from scratch

### Template Discovery Failure (Phase 18)
- Stale 34h server process failed to pick up new app templates
- Moved templates to root `templates/` directory; restart server after adding apps

### UUID vs BigInt Type Mismatch
- `person.id` returns UUID, must cast to `str(person.id)` before passing to services
- JWT middleware stores UUID as string; Django UUIDField coerces on lookup

### PermissionDenied vs PermissionDeniedException
- Kernel uses full name `PermissionDeniedException`
- Modules that import `PermissionDenied` will crash on first denial

---

## Known Open Items (Technical Debt)

1. **`dashboard/views_html.py`** — cross-module model imports (AttendanceSession, AdmissionApplication)
2. **`attendance/views_html.py`** — cross-module model import (ClassGroup)
3. **`AttendanceMarkingService.mark_bulk()`** — enrollment validation skipped (1 test skipped)
4. **`convert_to_enrollment`** — stub only, not wired to EnrollmentService
5. **`academics/assessments/create/`** — wrong permission code
6. **GCQ-000001–000003** — used by system accounts; students start at GCQ-000006

---

## Key Design Decisions

- **Person ≠ UserAccount**: One person can have multiple login methods; Person is permanent
- **UUID for Person PK**: Immutable, no sequential ID leakage, distributed-system safe
- **UserRoleBinding**: Temporal roles with PostgreSQL ExclusionConstraint (GiST) — mathematically impossible to have overlapping role assignments
- **Thread-local campus context**: Avoids passing campus_id everywhere; enables ORM auto-filtering
- **AuthorizationFacade**: Unified in `kernel.facades`, replaces 6 local duplicates
- **Celery + Redis**: Background tasks with explicit campus_id passing (no request context in workers)
- **JWT for API, Session for HTML**: Two auth paths — Bearer tokens for API, session cookies for browser views
- **Biometric Bridge**: WebSocket service (`bridge/server.py`) for USB scanner communication; Plugin architecture with MockDriver

---

## Test Status (Last Verified)

```
71 passed, 1 skipped, 0 failed (2026-03-27)
Profiles: 7 passed (2026-06-17)
```

---

## Environment

- **Python:** 3.12.10 (venv312)
- **Django:** 5.0
- **PostgreSQL:** 18.0 (database: `campus_platform_dev`)
- **Redis:** 3.0.504
- **Admin:** admin / admin123
- **Server:** http://127.0.0.1:8001/

---

## Source Files in Antigravity Brain

Located at `C:\Users\BactL\.gemini\antigravity-ide\brain\0b480c1a-b160-4af1-a038-84cda2691487\`:
- `project_log.md` — Full phase-by-phase development log
- `task.md` — Task tracker with open items
- `implementation_plan.md` — UI build plan for all 5 modules
- `walkthrough.md`, `walkthrough_phase8.md`, `walkthrough_phase9.md`, `walkthrough_phase10.md` — Phase walkthroughs
- `flowchart.md`, `system_flow.md` — Design docs
