from django.apps import AppConfig


class MediaAssetsConfig(AppConfig):
    name = 'modules.media'
    label = 'media_assets'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_register_permissions, sender=self)


def _register_permissions(sender, **kwargs):
    from kernel.models import Permission
    perms = [
        ('media.upload_media', 'Can upload media assets'),
        ('media.view_media', 'Can view media assets'),
        ('media.delete_media', 'Can delete media assets'),
    ]
    for code, name in perms:
        Permission.objects.get_or_create(
            code=code,
            defaults={'name': name, 'module': 'media_assets'}
        )
