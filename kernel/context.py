"""
Thread-Local Context Management

Provides thread-safe storage for request-scoped context variables.
Each HTTP request runs in its own thread, so context is isolated per request.
"""
import threading
from typing import Optional
from uuid import UUID

# Thread-local storage
_thread_locals = threading.local()


def set_current_campus_id(campus_id: int) -> None:
    """
    Set the current campus ID for this thread.
    
    Args:
        campus_id: ID of the campus to set as current context
    """
    _thread_locals.campus_id = campus_id


def get_current_campus_id() -> Optional[int]:
    """
    Get the current campus ID for this thread.
    
    Returns:
        Campus ID if set, None otherwise
    """
    return getattr(_thread_locals, 'campus_id', None)


def clear_campus_context() -> None:
    """
    Clear the campus context for this thread.
    
    Should be called after each request to prevent context leakage.
    """
    if hasattr(_thread_locals, 'campus_id'):
        delattr(_thread_locals, 'campus_id')
    if hasattr(_thread_locals, 'person_id'):
        delattr(_thread_locals, 'person_id')


def set_current_person_id(person_id: UUID) -> None:
    """
    Set the current person ID for this thread.
    
    Used for audit trails and logging.
    
    Args:
        person_id: UUID of the person to set as current context
    """
    _thread_locals.person_id = person_id


def get_current_person_id() -> Optional[UUID]:
    """
    Get the current person ID for this thread.
    
    Returns:
        Person UUID if set, None otherwise
    """
    return getattr(_thread_locals, 'person_id', None)


def get_context_info() -> dict:
    """
    Get all context information for debugging.
    
    Returns:
        Dictionary with campus_id and person_id
    """
    return {
        'campus_id': get_current_campus_id(),
        'person_id': get_current_person_id(),
    }
