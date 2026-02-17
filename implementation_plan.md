# Implementation Plan: UserRoleBinding Hardening (COMPLETED)

**Status:** ✅ Delivered on 2026-02-17

**Goal:** Make `UserRoleBinding` constitutionally final and PostgreSQL-correct as per specific user instructions.

## User Review Required
> [!IMPORTANT]
> This hardening phase enforces strict data integrity.
> - **Default Validity:** `validity` will default to `[now, infinity)`.
> - **GIST Index:** Explicitly specified in `ExclusionConstraint`.
> - **Deactivation:** Setting `is_active=False` will automatically close the `validity` range at `now`.
> - **Cleanup:** `valid_from` and `valid_until` references will be removed.

## Proposed Changes

### 1. Model Update
#### [MODIFY] [user_role_binding.py](file:///E:/The%20CMS/kernel/models/user_role_binding.py)
- **Default Value:** Set `validity` default to `DateTimeTZRange(timezone.now(), None, '[]')`.
- **GIST Index:** Update `ExclusionConstraint` to include `index_type='GIST'`.
- **Logic Fix:** Rewrite `is_currently_valid` to use `self.validity.contains(timezone.now())`.
- **Deactivation Logic:** Override `save()` method:
  ```python
  def save(self, *args, **kwargs):
      if not self.is_active and self.validity and self.validity.upper is None:
          # Close the range at now
          self.validity = DateTimeTZRange(self.validity.lower, timezone.now(), bounds='[)')
      super().save(*args, **kwargs)
  ```
- **Cleanup:** Remove any legacy property accessors if they still exist.

### 2. Migration
- Create migration `0009_harden_user_role_binding`.

### 3. Verification
- Update `test_temporal_constraints.py` to verify:
  - Default value behavior.
  - Deactivation closes the range.
  - `is_currently_valid` works correctly.
