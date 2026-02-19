
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AdmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.admissions'
    verbose_name = 'Admissions Module'

    def ready(self):
        """
        Constitution 5.2: Register permissions on app ready.
        """
        post_migrate.connect(self.register_permissions, sender=self)

    def register_permissions(self, sender, **kwargs):
        from kernel.models import Permission
        from .permissions import ADMISSIONS_PERMISSIONS

        for code, name in ADMISSIONS_PERMISSIONS:
            Permission.objects.get_or_create(
                module='admissions',
                code=code,
                defaults={'name': name, 'description': name}
            )
