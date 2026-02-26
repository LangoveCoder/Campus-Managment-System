from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AcademicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.academics'
    
    def ready(self):
        """Register permissions with kernel on startup."""
        post_migrate.connect(self.register_permissions, sender=self)
    
    def register_permissions(self, sender, **kwargs):
        try:
            from kernel.models import Permission
            from .permissions import ACADEMIC_PERMISSIONS
            
            for code, name, is_dangerous in ACADEMIC_PERMISSIONS:
                Permission.objects.get_or_create(
                    module='academics',
                    code=code,
                    defaults={
                        'name': name,
                        'description': f'Academic module permission: {name}',
                        'is_dangerous': is_dangerous
                    }
                )
        except Exception:
            # Avoid breaking initial migrations if tables don't exist
            pass
