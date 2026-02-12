from django.db import transaction
from django.utils import timezone
from kernel.models import AuditLog, Person, Campus, Role
import json

class AuditService:
    """
    Service for creating and retrieving audit logs.
    """
    
    @staticmethod
    def log_action(
        action: str,
        actor_person_id=None,
        campus_id=None,
        role_id=None,
        target_type: str = None,
        target_id: str = None,
        changes: dict = None,
        ip_address: str = None,
        result: str = 'SUCCESS',
        reason: str = None,
        user_agent: str = None
    ) -> AuditLog:
        """
        Create an immutable audit log entry.
        
        Args:
            action: Name of the action (e.g., 'create_student')
            actor_person_id: ID of the person performing the action (optional)
            campus_id: ID of the campus where action occurred (optional)
            role_id: ID of the role used (optional)
            target_type: Type of entity being affected (optional)
            target_id: ID of entity being affected (optional)
            changes: Dictionary of changes (optional)
            ip_address: IP address of the request (optional)
            result: 'SUCCESS', 'FAILURE', or 'DENIED'
            reason: Reason for failure/denial (optional)
            user_agent: User agent string (optional)
            
        Returns:
            The created AuditLog instance
        """
        try:
            # Resolve foreign keys if IDs are provided
            actor = None
            if actor_person_id:
                try:
                    actor = Person.objects.get(id=actor_person_id)
                except Person.DoesNotExist:
                    pass
                    
            campus = None
            if campus_id:
                try:
                    campus = Campus.objects.get(id=campus_id)
                except Campus.DoesNotExist:
                    pass
            
            role = None
            if role_id:
                try:
                    role = Role.objects.get(id=role_id)
                except Role.DoesNotExist:
                    pass

            # Create the log entry
            log = AuditLog.objects.create(
                action=action,
                actor=actor,
                campus=campus,
                role=role,
                target_type=target_type,
                target_id=str(target_id) if target_id else None,
                changes=changes,
                ip_address=ip_address,
                result=result,
                reason=reason,
                user_agent=user_agent
            )
            return log
            
        except Exception as e:
            # Fallback logging if database write fails
            # We don't want audit failure to crash the application, 
            # but we must log it somewhere (e.g. file system)
            print(f"CRITICAL: Failed to write audit log: {e}")
            return None

    @staticmethod
    def log_permission_check(
        person_id,
        campus_id,
        permission: str,
        granted: bool,
        ip_address: str = None
    ):
        """
        Helper to specifically log permission checks.
        """
        result = 'SUCCESS' if granted else 'DENIED'
        
        AuditService.log_action(
            action='permission_check',
            actor_person_id=person_id,
            campus_id=campus_id,
            target_type='Permission',
            target_id=permission,
            result=result,
            ip_address=ip_address
        )

    @staticmethod
    def get_logs_for_person(person_id, limit=50):
        """Get recent logs for a specific person"""
        return AuditLog.objects.filter(actor_id=person_id)[:limit]

    @staticmethod
    def get_logs_for_entity(target_type, target_id, limit=50):
        """Get history for a specific entity"""
        return AuditLog.objects.filter(
            target_type=target_type, 
            target_id=str(target_id)
        )[:limit]
