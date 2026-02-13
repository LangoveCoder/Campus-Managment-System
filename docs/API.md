# API Reference - Campus Management Platform

## Base URL
`http://localhost:8001/api/`

## Authentication
All endpoints require a valid session cookie (Standard Django Auth).

---

## 1. Biometric Operations

### 1.1 Enroll Biometrics
**POST** `/biometric/enroll`

Enrolls a user's biometric template.

**Payload:**
```json
{
    "person_id": "uuid-string",
    "biometric_type": "FINGERPRINT", // or FACE, IRIS
    "biometric_data": "base64-encoded-string"
}
```

**Response (200 OK):**
```json
{
    "status": "success",
    "message": "Biometric enrolled successfully",
    "biometric_id": 123
}
```

**Errors:**
*   `400 Bad Request`: Missing fields or low quality.
*   `403 Forbidden`: User does not have permission to enroll.

---

### 1.2 Authenticate Biometrics
**POST** `/biometric/auth`

Identifies a user from a biometric scan.

**Payload:**
```json
{
    "biometric_type": "FINGERPRINT",
    "biometric_data": "base64-encoded-string"
}
```

**Response (200 OK):**
```json
{
    "status": "success",
    "person_id": "uuid-string",
    "confidence": 0.98
}
```

**Errors:**
*   `404 Not Found`: No match found.

---

## 2. Context Management

### 2.1 Switch Campus Context
**POST** `/context/switch`

Changes the active campus for the current session.

**Payload:**
```json
{
    "campus_id": 1
}
```

**Response (200 OK):**
```json
{
    "status": "success",
    "active_campus_id": 1,
    "active_campus_name": "Main Campus"
}
```

**Errors:**
*   `403 Forbidden`: User does not have an active role binding for this campus.
