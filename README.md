# Campus Management Identity System (CMP-Identity)

**Version:** 1.0.0
**Status:** Production Ready

A modular, secure, and compliant Identity Management System built with Django and a custom Hardware Bridge for biometric integration.

## 🚀 Quick Start

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

3.  **Seed Data:**
    ```bash
    python scripts/seed_permissions.py
    python scripts/seed_role_permissions.py
    ```

4.  **Start Server:**
    ```bash
    python manage.py runserver 8001
    ```

5.  **Start Hardware Bridge (for Biometrics):**
    ```bash
    cd bridge
    python server.py
    ```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

*   **[Developer Guide](docs/DEVELOPER.md):** Architecture, detailed setup, and testing.
*   **[API Reference](docs/API.md):** Endpoints and payloads.
*   **[Deployment Guide](docs/DEPLOYMENT.md):** Production setup instructions.
*   **[User Guide](docs/USER_GUIDE.md):** Admin manual.

## 🏗️ Architecture

*   **Kernel:** Modular Monolith (Django) handling Identity, Auth, and Context.
*   **Bridge:** WebSocket service for communicating with local USB hardware.
*   **Security:** Middleware-enforced Campus Context Isolation.

## 🧪 Testing

Run the full test suite:
```bash
python manage.py test
```

Run specific integration tests:
```bash
python manage.py test kernel.tests.test_integration_full
```
