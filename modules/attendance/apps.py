
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.attendance'
    verbose_name = 'Attendance Module'

    def ready(self):
        """
        Register permissions on app ready.
        """
        post_migrate.connect(self.register_permissions, sender=self)

    def register_permissions(self, sender, **kwargs):
        from kernel.models import Permission
        from .permissions import ATTENDANCE_PERMISSIONS

        for code, name in ATTENDANCE_PERMISSIONS:
            full_code = f"attendance.{code}"
            Permission.objects.get_or_create(
                module='attendance',
                code=full_code,
                defaults={'name': name, 'description': name}
            )
