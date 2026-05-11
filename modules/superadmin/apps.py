from django.apps import AppConfig


class SuperAdminConfig(AppConfig):
    name = 'modules.superadmin'
    label = 'superadmin'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_register_permissions, sender=self)


def _register_permissions(sender, **kwargs):
    from kernel.models import Permission
    perms = [
        ('superadmin.manage_campuses', 'Can manage campuses'),
    ]
    for code, label in perms:
        Permission.objects.get_or_create(
            code=code,
            defaults={'label': label}
        )
