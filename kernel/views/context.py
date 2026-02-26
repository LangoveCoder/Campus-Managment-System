"""
Campus Context Views

Views for campus selection and switching.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from kernel.services import RoleBindingService


@login_required
def select_campus(request):
    """
    View for selecting campus context.
    
    Displays all campuses where the user has active role bindings.
    User selects one campus to set as their current context.
    """
    if request.method == 'POST':
        campus_id = request.POST.get('campus_id')
        if campus_id:
            # Verify user has access to this campus
            person = request.user.person
            bindings = RoleBindingService.get_bindings_for_person(
                person_id=person.id,
                active_only=True
            )
            
            campus_ids = [b.campus_id for b in bindings]
            if int(campus_id) in campus_ids:
                # Set campus in session
                request.session['current_campus_id'] = int(campus_id)
                return redirect('/dashboard/')
    
    # GET request - show campus selection form
    person = request.user.person
    bindings = RoleBindingService.get_bindings_for_person(
        person_id=person.id,
        active_only=True
    )
    
    # Group bindings by campus with role info
    campus_roles = {}
    for binding in bindings:
        campus = binding.campus
        if campus.id not in campus_roles:
            campus_roles[campus.id] = {
                'campus': campus,
                'roles': []
            }
        campus_roles[campus.id]['roles'].append(binding.role.name)
    
    return render(request, 'kernel/select_campus.html', {
        'campus_roles': campus_roles.values(),
        'title': 'Select Campus'
    })


@login_required
@require_http_methods(["POST"])
def switch_campus(request):
    """
    API endpoint to switch campus context.
    
    Accepts JSON payload with campus_id.
    Verifies user has access to the campus.
    Updates session with new campus_id.
    """
    try:
        data = json.loads(request.body)
        campus_id = data.get('campus_id')
        
        if not campus_id:
            return JsonResponse({'success': False, 'error': 'campus_id required'}, status=400)
        
        # Verify user has access to this campus
        person = request.user.person
        bindings = RoleBindingService.get_bindings_for_person(
            person_id=person.id,
            active_only=True
        )
        
        campus_ids = [b.campus_id for b in bindings]
        if int(campus_id) in campus_ids:
            request.session['current_campus_id'] = int(campus_id)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

