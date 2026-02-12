from functools import wraps
from .services.audit_service import AuditService
from .context import get_current_campus_id, get_current_person_id

def audit_action(action_name=None):
    """
    Decorator to automatically log service method calls.
    
    Usage:
        @audit_action(action_name="create_student")
        def create_student(self, ...):
            ...
            
    If action_name is not provided, it defaults to the method name.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine action name
            nonlocal action_name
            if not action_name:
                action_name = func.__name__

            # Capture context
            person_id = get_current_person_id()
            campus_id = get_current_campus_id()

            # Execute the function
            try:
                result = func(*args, **kwargs)
                
                # Log success
                AuditService.log_action(
                    action=action_name,
                    actor_person_id=person_id,
                    campus_id=campus_id,
                    result='SUCCESS',
                    # We could try to serialize args/kwargs here for 'changes'
                    # but that might be heavy or contain sensitive data
                    reason=f"Method {action_name} completed successfully"
                )
                return result
                
            except Exception as e:
                # Log failure
                AuditService.log_action(
                    action=action_name,
                    actor_person_id=person_id,
                    campus_id=campus_id,
                    result='FAILURE',
                    reason=str(e)
                )
                raise e
                
        return wrapper
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
            
            # Note: This is a simplified logger.
            # Real permission enforcement happens inside the service/view.
            # This decorator is best used when we want to EXPLICITLY log
            # that a specific sensitive action was attempted.
            
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
