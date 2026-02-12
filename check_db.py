import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from kernel.models import Permission, Role, RolePermissionMap
print("Permissions:", Permission.objects.count())
print("Roles:", Role.objects.count())
print("Mappings:", RolePermissionMap.objects.count())
