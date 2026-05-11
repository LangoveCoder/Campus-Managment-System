from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.hashers import make_password


def _is_superadmin(request):
    """Check if the current user has the SUPER_ADMIN role (not campus-scoped)."""
    person = getattr(request.user, 'person', None)
    if not person:
        return False
    from kernel.models import UserRoleBinding
    return UserRoleBinding.objects.filter(
        person=person,
        role__name='SUPER_ADMIN',
        is_active=True,
    ).exists()


@login_required
def campuses_view(request):
    if not _is_superadmin(request):
        return render(request, 'superadmin/403.html', status=403)

    from kernel.models import Campus, UserRoleBinding
    from modules.campus_identity.models import CampusIDConfig

    campuses = Campus.objects.all().order_by('id')

    # Build enriched list — one query each via annotation avoidance
    configs = {c.campus_id: c for c in CampusIDConfig.objects.all()}
    admin_counts = {}
    for binding in UserRoleBinding.objects.filter(role__name='CAMPUS_ADMIN', is_active=True).select_related('campus'):
        admin_counts[binding.campus_id] = admin_counts.get(binding.campus_id, 0) + 1

    campus_rows = []
    for campus in campuses:
        cfg = configs.get(campus.id)
        campus_rows.append({
            'campus': campus,
            'prefix': cfg.prefix if cfg else '—',
            'padding': cfg.padding if cfg else '—',
            'admin_count': admin_counts.get(campus.id, 0),
        })

    return render(request, 'superadmin/campuses.html', {
        'campus_rows': campus_rows,
        'active_section': 'superadmin',
        'is_superadmin': True,
    })


@login_required
def create_campus_view(request):
    if not _is_superadmin(request):
        return render(request, 'superadmin/403.html', status=403)

    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        city = request.POST.get('city', '').strip()
        contact_email = request.POST.get('contact_email', '').strip()
        prefix = request.POST.get('prefix', '').strip().upper()
        padding = int(request.POST.get('padding', 6))
        admin_full_name = request.POST.get('admin_full_name', '').strip()
        admin_phone = request.POST.get('admin_phone', '').strip()
        admin_password = request.POST.get('admin_password', '').strip()

        if not all([name, admin_full_name, admin_phone, admin_password]):
            error = "Campus name, admin full name, phone, and password are all required."
        else:
            try:
                with transaction.atomic():
                    from kernel.models import Campus, Person, UserAccount, Role, UserRoleBinding
                    from modules.campus_identity.services import CampusIdentityService

                    # 1. Create campus
                    campus = Campus.objects.create(
                        name=name,
                        campus_type='PHYSICAL',
                        address=city,
                    )

                    # 2. Setup ID config
                    CampusIdentityService.setup_config(
                        campus_id=str(campus.id),
                        prefix=prefix,
                        padding=padding,
                    )

                    # 3. Create Person + UserAccount for first admin
                    person = Person.objects.create(
                        full_name=admin_full_name,
                        primary_phone=admin_phone,
                        primary_email=contact_email or None,
                    )
                    username = admin_phone.replace('+', '').replace('-', '').replace(' ', '')[:20]
                    account = UserAccount.objects.create(
                        username=username,
                        person=person,
                        password=make_password(admin_password),
                        email=contact_email or '',
                    )

                    # 4. Assign CAMPUS_ADMIN role
                    role = Role.objects.get(name='CAMPUS_ADMIN')
                    UserRoleBinding.objects.create(
                        person=person,
                        role=role,
                        campus=campus,
                    )

                    # 5. Global fail-safe: grant all permissions to CAMPUS_ADMIN
                    from kernel.models import Permission, RolePermissionMap
                    all_perms = Permission.objects.all()
                    for perm in all_perms:
                        RolePermissionMap.objects.get_or_create(
                            role=role,
                            permission=perm,
                            defaults={'granted_by': None}
                        )

                return redirect('superadmin_campuses')

            except Exception as e:
                error = f"Error creating campus: {e}"

    return render(request, 'superadmin/create_campus.html', {
        'error': error,
        'active_section': 'superadmin',
        'is_superadmin': True,
    })


@login_required
def delete_campus_view(request, campus_id):
    if not _is_superadmin(request):
        return render(request, 'superadmin/403.html', status=403)

    if request.method != 'POST':
        return redirect('superadmin_campuses')

    from kernel.models import Campus, UserRoleBinding
    from modules.campus_identity.models import CampusIDConfig, CampusPerson

    try:
        campus = Campus.objects.get(id=campus_id)
    except Campus.DoesNotExist:
        return redirect('superadmin_campuses')

    # Safety check — no active enrollments
    from modules.academics.models import Enrollment
    active_enrollments = Enrollment.objects.filter(
        class_group__academic_cycle__academic_program__campus_id=campus_id,
        status='ACTIVE'
    ).count()
    if active_enrollments > 0:
        error = f"Cannot delete: campus has {active_enrollments} active enrollment(s)."
        # Re-render campuses view with error
        from kernel.models import Campus as CampusModel
        campuses = CampusModel.objects.all().order_by('id')
        configs = {c.campus_id: c for c in CampusIDConfig.objects.all()}
        admin_counts = {}
        for binding in UserRoleBinding.objects.filter(role__name='CAMPUS_ADMIN', is_active=True).select_related('campus'):
            admin_counts[binding.campus_id] = admin_counts.get(binding.campus_id, 0) + 1
        campus_rows = []
        for c in campuses:
            cfg = configs.get(c.id)
            campus_rows.append({
                'campus': c,
                'prefix': cfg.prefix if cfg else '—',
                'padding': cfg.padding if cfg else '—',
                'admin_count': admin_counts.get(c.id, 0),
            })
        return render(request, 'superadmin/campuses.html', {
            'campus_rows': campus_rows,
            'active_section': 'superadmin',
            'is_superadmin': True,
            'error': error,
        })

    with transaction.atomic():
        CampusPerson.objects.filter(campus_id=campus_id).delete()
        CampusIDConfig.objects.filter(campus_id=campus_id).delete()
        UserRoleBinding.objects.filter(campus=campus).delete()
        campus.delete()

    return redirect('superadmin_campuses')

