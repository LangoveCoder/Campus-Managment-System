from django.core.management.base import BaseCommand
from kernel.models import Role

class Command(BaseCommand):
    help = 'Seeds the database with default system roles'

    def handle(self, *args, **options):
        roles_data = [
            ('SUPER_ADMIN', 'Super Administrator with full system access'),
            ('CAMPUS_ADMIN', 'Administrator for a specific campus'),
            ('REGISTRAR', 'Registrar responsible for student records'),
            ('FACULTY', 'Teaching staff'),
            ('STUDENT', 'Enrolled student'),
            ('PARENT', 'Parent or guardian'),
            ('ACCOUNTANT', 'Financial officer'),
            ('LIBRARIAN', 'Library staff'),
            ('SECURITY', 'Security personnel'),
        ]

        for name, description in roles_data:
            role, created = Role.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Role already exists: {name}'))
