"""
Custom Django Managers

Provides custom managers for automatic query filtering and scoping.
"""
from django.db import models
from .context import get_current_campus_id


class CampusAwareManager(models.Manager):
    """
    Manager that automatically filters queries by current campus context.
    
    When a campus context is set (via middleware), all queries using this
    manager will automatically filter by campus_id. This ensures data
    isolation and prevents accidental cross-campus data access.
    
    Usage:
        class Student(BaseCampusModel):
            name = models.CharField(max_length=200)
            # Inherits objects = CampusAwareManager()
        
        # With campus context set to campus_id=1
        Student.objects.all()  # Only returns campus 1 students
        Student.objects.all_campuses()  # Returns all students (bypass filter)
    """
    
    def get_queryset(self):
        """
        Override get_queryset to add campus filtering.
        
        Returns:
            QuerySet filtered by current campus_id if context is set
        """
        qs = super().get_queryset()
        campus_id = get_current_campus_id()
        
        # Only filter if campus context is set
        if campus_id is not None:
            return qs.filter(campus_id=campus_id)
        
        return qs
    
    def all_campuses(self):
        """
        Bypass campus filtering and return all records.
        
        Use this when you explicitly need to query across all campuses,
        such as in admin views or reports.
        
        Returns:
            Unfiltered QuerySet with all records
        """
        return super().get_queryset()
    
    def for_campus(self, campus_id: int):
        """
        Explicitly query for a specific campus.
        
        Bypasses the current context and queries for the specified campus.
        
        Args:
            campus_id: ID of the campus to query
            
        Returns:
            QuerySet filtered by specified campus_id
        """
        return super().get_queryset().filter(campus_id=campus_id)
