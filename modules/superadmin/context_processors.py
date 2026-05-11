def superadmin_context(request):
    """Inject is_superadmin and has_campus_admin flags into every template context."""
    if not request.user.is_authenticated:
        return {'is_superadmin': False, 'has_campus_admin': False}
    person = getattr(request.user, 'person', None)
    if not person:
        return {'is_superadmin': False, 'has_campus_admin': False}
    from kernel.models import UserRoleBinding
    
    bindings = UserRoleBinding.objects.filter(person=person, is_active=True).values_list('role__name', flat=True)
    
    is_sa = 'SUPER_ADMIN' in bindings
    has_ca = 'CAMPUS_ADMIN' in bindings
    
    return {
        'is_superadmin': is_sa,
        'has_campus_admin': has_ca,
    }
