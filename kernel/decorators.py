from functools import wraps
from .services.audit_service import AuditService
from .context import get_current_campus_id, get_current_person_id

def audit_action(action=None, target_type=None, **audit_kwargs):
    """
    Decorator to automatically log service method calls.
    
    Usage:
        @audit_action
        def my_method(self): ...
        
        @audit_action(action="create_student", target_type="Person")
        def create_student(self): ...
    """
    def _create_wrapper(func, action_name, target_type_val):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine action name
            actual_action = action_name or func.__name__

            # Capture context
            person_id = get_current_person_id()
            campus_id = get_current_campus_id()

            # Execute the function
            try:
                result = func(*args, **kwargs)
                
                # Log success
                AuditService.log_action(
                    action=actual_action,
                    actor_person_id=person_id,
                    campus_id=campus_id,
                    target_type=target_type_val,
                    result='SUCCESS',
                    reason=f"Method {actual_action} completed successfully"
                )
                return result
                
            except Exception as e:
                # Log failure
                AuditService.log_action(
                    action=actual_action,
                    actor_person_id=person_id,
                    campus_id=campus_id,
                    target_type=target_type_val,
                    result='FAILURE',
                    reason=str(e)
                )
                raise e
        return wrapper

    if callable(action):
        # Called as @audit_action without arguments
        return _create_wrapper(action, None, None)
    else:
        # Called as @audit_action(...)
        def decorator(func):
            return _create_wrapper(func, action, target_type)
        return decorator

def audit_permission(permission_required):
    """
    Decorator to log permission checks on Views or Service methods.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            person_id = get_current_person_id()
            campus_id = get_current_campus_id()
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # If the function raises PermissionDenied, we log it
                if "PermissionDenied" in type(e).__name__:
                    AuditService.log_permission_check(
                        person_id, campus_id, permission_required, granted=False
                    )
                raise e
        return wrapper
    return decorator
