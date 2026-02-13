# Deployment Guide - Campus Management Platform

## 1. Production Requirements

*   **OS:** Ubuntu 22.04 LTS or Windows Server 2022
*   **Python:** 3.12.x
*   **Database:** PostgreSQL 14+
*   **Broker:** Redis 6+ (for Channels/WebSocket)
*   **Web Server:** Nginx (Reverse Proxy) + Gunicorn (WSGI) + Daphne (ASGI)

## 2. Environment Variables (`.env`)

Create a `.env` file in the project root:

```ini
DEBUG=False
SECRET_KEY=production-secret-key-change-this
ALLOWED_HOSTS=campus-platform.com,10.0.0.5

# Database
DB_NAME=campus_prod
DB_USER=campus_admin
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1
```

## 3. Database Migration

On the production server:

```bash
# 1. Apply schema changes
python manage.py migrate

# 2. Collect static files (CSS/JS)
python manage.py collectstatic --noinput

# 3. Seed initial permissions
python seed_permissions.py
python seed_role_permissions.py
```

## 4. Serving the Application

We need **two** processes: one for standard HTTP (Gunicorn) and one for WebSockets (Daphne).

### 4.1 Gunicorn (HTTP)
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### 4.2 WebSocket Bridge
The WebSocket functionality is handled by the standalone Bridge service (see Section 5). The main Django application does not need a separate ASGI server for this architecture.

## 5. Hardware Bridge Deployment

The Hardware Bridge must run **locally** on the client machine where the USB scanner is attached.

1.  **Install Python 3.12** on the client PC.
2.  **Copy `bridge/` folder** to the client.
3.  **Install Dependencies:** `pip install -r requirements.txt`
4.  **Run Server:** `python server.py`
5.  **Auto-Start:** Add a shortcut to `shell:startup` on Windows to run `pythonw server.py` (headless).
