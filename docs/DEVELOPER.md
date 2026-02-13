# Developer Guide - Campus Management Platform

## 1. System Architecture

The Identity System is built on a **Modular Monolith** architecture using Django.

### Core Components
*   **Kernel (`kernel/`)**: Contains the core business logic, models, and services.
    *   **Models**: `Person` (Immutable Identity), `UserAccount` (Auth), `UserRoleBinding` (Authorization).
    *   **Services**: `IdentityService`, `AuthorizationService`, `BiometricService`.
    *   **Middleware**: `CampusContextMiddleware` (Handles strict data isolation per campus).
*   **Bridge (`bridge/`)**: A standalone Python WebSocket server for hardware integration.
    *   **Drivers**: Plugin system for USB scanners (currently using `MockDriver`).

### Data Flow
1.  **Request**: User hits an endpoint (e.g., `/api/biometric/enroll`).
2.  **Middleware**: Resolves `active_campus_id` from session.
3.  **View**: Calls `BiometricService`.
4.  **Service**: Validates input -> Checks Permissions -> Updates DB.
5.  **Audit**: `@audit_action` decorator logs the event to `AuditLog`.

---

## 2. Setup Instructions

### Prerequisites
*   Python 3.12+
*   PostgreSQL 14+
*   Redis (for caching/sessions)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <repo_url>
    cd cmp-identity
    ```

2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv312
    .\venv312\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Setup:**
    *   Create a Postgres DB named `campus_platform_dev`.
    *   Run migrations:
        ```bash
        python manage.py migrate
        ```

5.  **Seed Data:**
    ```bash
    python seed_permissions.py
    python seed_role_permissions.py
    ```

6.  **Run Server:**
    ```bash
    python manage.py runserver 8001
    ```

---

## 3. Testing

### Running Tests
We use Django's test runner extended with custom suites.

*   **Run All Tests:**
    ```bash
    python manage.py test
    ```

*   **Run Integration Suite (Phase 6):**
    ```bash
    python manage.py test kernel.tests.test_integration_full
    ```

*   **Run Security Audit:**
    ```bash
    python security_audit.py
    ```

*   **Run Load Test:**
    ```bash
    python load_test.py
    ```

---

## 4. Hardware Bridge

To develop with biometric hardware:

1.  **Navigate to Bridge:**
    ```bash
    cd bridge
    ```

2.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Server:**
    ```bash
    python server.py
    ```
    *   Default Port: `15432`
    *   Default Driver: `mock` (Simulation)

4.  **Configuration:**
    Edit `bridge/config.json` to change drivers (e.g., to `secugen` or `zkteco` in future).
