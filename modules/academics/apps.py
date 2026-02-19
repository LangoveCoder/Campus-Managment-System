from django.apps import AppConfig

class AcademicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.academics'
    
    def ready(self):
        """Register permissions with kernel on startup."""
        self.register_permissions()
    
    def register_permissions(self):
        try:
            from kernel.models import Permission
            from .permissions import ACADEMIC_PERMISSIONS
            
            for code, name, is_dangerous in ACADEMIC_PERMISSIONS:
                Permission.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'module': 'academics',
                        'description': f'Academic module permission: {name}',
                        'is_dangerous': is_dangerous
                    }
                )
        except Exception:
            # Avoid breaking initial migrations if tables don't exist
            pass
