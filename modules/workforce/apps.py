
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class WorkforceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.workforce'
    verbose_name = 'Workforce Attendance Module'

    def ready(self):
        post_migrate.connect(self.register_permissions, sender=self)

    def register_permissions(self, sender, **kwargs):
        from django.apps import apps
        Permission = apps.get_model('kernel', 'Permission')
        from .permissions import WORKFORCE_PERMISSIONS

        for code, name in WORKFORCE_PERMISSIONS:
            full_code = f"workforce.{code}"
            Permission.objects.get_or_create(
                module='workforce',
                code=full_code,
                defaults={'name': name, 'description': name}
            )
