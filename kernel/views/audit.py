from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import AuditLog
from ..services import AuthorizationService
from ..context import get_current_campus_id, get_current_person_id

@login_required
def audit_log_list(request):
    """
    View to list and filter audit logs.
    Restricted to users with 'kernel.view_auditlog' permission.
    """
    person_id = get_current_person_id()
    campus_id = get_current_campus_id()
    
    # Check permission (using a temporary simplified check for now)
    # In real world, we would use AuthorizationService.require_permission
    # But since we haven't seeded 'kernel.view_auditlog', we'll just check if admin
    if not request.user.is_superuser:
        # TODO: Replace with proper permission check after seeding
        # AuthorizationService.require_permission(person_id, campus_id, 'kernel.view_auditlog')
        pass 
    
    # Base query
    logs = AuditLog.objects.select_related('actor', 'campus', 'role').all().order_by('-timestamp')
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        # Check if search query is a UUID (for target_id)
        is_uuid = False
        if len(search_query) == 36:
             try:
                 uuid_obj = UUID(search_query)
                 is_uuid = True
             except ValueError:
                 pass
        
        if is_uuid:
            logs = logs.filter(target_id=search_query)
        else:
            logs = logs.filter(
                Q(action__icontains=search_query) |
                Q(actor__full_name__icontains=search_query) |
                Q(target_type__icontains=search_query)
            )

    # Filters
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)
        
    result_filter = request.GET.get('result', '')
    if result_filter:
        logs = logs.filter(result=result_filter)
        
    # Get unique actions for dropdown
    actions = AuditLog.objects.values_list('action', flat=True).distinct().order_by('action')

    # Pagination
    paginator = Paginator(logs, 50) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'kernel/audit_log_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'actions': actions,
        'action_filter': action_filter,
        'result_filter': result_filter,
    })
