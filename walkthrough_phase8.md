# Walkthrough: Phase 8 - Temporal Upgrade & Hardening

## Overview
We upgraded the `UserRoleBinding` model to use **PostgreSQL Native Exclusion Constraints** to enforce strict temporal exclusivity. This prevents any possibility of overlapping role assignments for the same person/role/campus combination.

## Key Changes

### 1. Database Schema
- **New Field:** `validity` (DateTimeRangeField) replaces `valid_from` and `valid_until`.
- **Constraint:** `ExclusionConstraint` ensures `validity` ranges do not overlap.
- **Index:** Explicit `GIST` index for performance and constraint enforcement.
- **Default:** Validity defaults to `[now, infinity)`.

### 2. Migration Strategy
We performed a safe, multi-step migration:
1.  **Add Field:** Added `validity` (nullable).
2.  **Data Migration:** Copied existing `valid_from`/`valid_until` data into `validity` ranges.
3.  **Finalize:** Removed old fields, made `validity` required, and applied constraints.
4.  **Hardening:** Enforced constitutional rules (deactivation closes range).

### 3. Verification
We verified the logic with `tests/test_temporal_constraints.py`:

| Test Case | Expectation | Result |
| :--- | :--- | :--- |
| **Basic Binding** | Create valid range | ✅ Passed |
| **Overlap Prevention** | **REJECT** overlapping range | ✅ Passed (IntegrityError raised) |
| **Adjacent Periods** | Allow ranges that touch (end == start) | ✅ Passed |
| **Different Roles** | Allow overlaps for different roles | ✅ Passed |
| **Open-Ended** | Handle infinite end dates correctly | ✅ Passed |
| **Default Validity** | Default to `[now, infinity)` | ✅ Passed |
| **Deactivation** | Auto-close range when `is_active=False` | ✅ Passed |

## Constitutional Rule: Deactivation
We implemented a strict rule: **Deactivation must close the validity range.**
```python
def save(self, *args, **kwargs):
    if not self.is_active and self.validity and self.validity.upper is None:
        # Close the range at now
        self.validity = DateTimeTZRange(self.validity.lower, timezone.now(), bounds='[)')
    super().save(*args, **kwargs)
```

## Conclusion
The Identity Engine is now **Constitutionally Correct** regarding legacy rules. The database itself prevents corruption.
