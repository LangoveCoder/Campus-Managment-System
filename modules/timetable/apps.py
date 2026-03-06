from django.apps import AppConfig


class TimetableConfig(AppConfig):
    name = 'modules.timetable'
    label = 'timetable'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_register_permissions, sender=self)


def _register_permissions(sender, **kwargs):
    from kernel.models import Permission
    perms = [
        ('timetable.view_timetable', 'Can view timetable'),
        ('timetable.manage_timetable', 'Can manage timetable slots'),
    ]
    for code, name in perms:
        Permission.objects.get_or_create(
            code=code,
            defaults={'name': name, 'module': 'timetable'}
        )
