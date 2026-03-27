from django.apps import AppConfig


class CampusIdentityConfig(AppConfig):
    name = 'modules.campus_identity'
    label = 'campus_identity'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_register_permissions, sender=self)


def _register_permissions(sender, **kwargs):
    from kernel.models import Permission
    perms = [
        ('campus_identity.view_identity', 'Can view campus identity records'),
        ('campus_identity.manage_identity', 'Can manage campus identity assignments'),
    ]
    for code, name in perms:
        Permission.objects.get_or_create(
            code=code,
            defaults={'name': name, 'module': 'campus_identity'}
        )
