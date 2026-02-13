# User Guide - Campus Management Platform

## 1. Getting Started

### Login
1.  Navigate to the Homepage.
2.  Enter your **Username** and **Password**.
   *   *Default Admin:* `admin` / `admin123`

### Dashboard
The Dashboard shows your active Campus Context.
*   **Switching Campuses:** Use the "Switch Campus" dropdown in the top navigation bar to change your view if you work at multiple locations.

---

## 2. Managing Users (Admin)

### 2.1 Onboarding a New Student
1.  Go to **Admin Panel** (`/admin/`).
2.  **Persons**: Click "Add Person".
    *   Enter Full Name, Email, Phone.
    *   *Note:* This creates the unique identity.
3.  **User Accounts**: Click "Add User Account".
    *   Link the Person you just created.
    *   Set a temporary password.
4.  **User Role Bindings**: Click "Add Binding".
    *   Select **Person**.
    *   Select **Role** (e.g., `student`).
    *   Select **Campus** (e.g., `Main Campus`).
    *   Set **Valid From** to "Today".

---

## 3. Biometrics

### 3.1 Enrolling a User
1.  Ensure the **Hardware Bridge** is running on your PC (Green icon in system tray - *Future Feature*).
2.  Navigate to **Biometric Enrollment**.
3.  Enter the **Person ID** (UUID) or search for the user.
4.  Click **"Start Scan"**.
5.  Ask the user to place their finger on the scanner.
6.  Wait for the **"Success" (Green Check)** message.

### 3.2 Troubleshooting
*   **"Driver Error"**:
    *   Check if `server.py` is running on your machine.
    *   Verify the USB scanner is plugged in.
    *   Refresh the page.

---

## 4. Audit Logs

To view system activity:
1.  Go to `/audit/`.
2.  **Filter By:**
    *   **Action:** `auth.login`, `biometric.enroll`, `access.denied`
    *   **Status:** `SUCCESS` or `FAILURE`
3.  Click `View Details` to see exactly what changed.
