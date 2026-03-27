"""
CampusIdentityService — generates and manages campus-scoped person identifiers.

Constitutional rule: all ORM lives here. Views must not touch models directly.
Transaction safety: select_for_update() on CampusIDConfig prevents duplicate sequences
under concurrent requests.
"""
from django.db import transaction


class CampusIdentityService:

    @staticmethod
    @transaction.atomic
    def add_person_to_campus(person_id: str, campus_id: str):
        """
        Assign a permanent campus identifier to a person.

        - Locks CampusIDConfig row via select_for_update() to prevent races.
        - Generates next identifier atomically.
        - Is idempotent: if CampusPerson already exists, returns existing record.

        Args:
            person_id: str UUID of the kernel.Person
            campus_id: str UUID of the campus

        Returns:
            CampusPerson instance
        """
        from modules.campus_identity.models import CampusIDConfig, CampusPerson
        from kernel.models import Person

        # Idempotency: return existing if already enrolled
        try:
            return CampusPerson.objects.get(
                campus_id=campus_id,
                person_id=person_id,
            )
        except CampusPerson.DoesNotExist:
            pass

        # Lock the config row to prevent duplicate sequence under concurrent requests
        config = (
            CampusIDConfig.objects
            .select_for_update()
            .get(campus_id=campus_id)
        )

        # Generate next identifier
        sequence = config.current_sequence + 1
        number = str(sequence).zfill(config.padding)
        identifier = f"{config.prefix}-{number}" if config.prefix else number

        # Persist sequence increment
        config.current_sequence = sequence
        config.save(update_fields=['current_sequence'])

        # Create the CampusPerson record
        person = Person.objects.get(id=person_id)
        campus_person = CampusPerson.objects.create(
            campus_id=campus_id,
            person=person,
            campus_identifier=identifier,
        )
        return campus_person

    @staticmethod
    def get_campus_person(person_id: str, campus_id: str):
        """Return CampusPerson or None."""
        from modules.campus_identity.models import CampusPerson
        try:
            return CampusPerson.objects.get(
                campus_id=campus_id,
                person_id=person_id,
            )
        except CampusPerson.DoesNotExist:
            return None

    @staticmethod
    def get_identifier(person_id: str, campus_id: str) -> str | None:
        """Return the campus identifier string, or None if not enrolled."""
        cp = CampusIdentityService.get_campus_person(person_id, campus_id)
        return cp.campus_identifier if cp else None

    @staticmethod
    @transaction.atomic
    def setup_config(campus_id: str, prefix: str = '', padding: int = 6):
        """
        Create or update CampusIDConfig for a campus.
        Does NOT reset current_sequence if config already exists.

        Args:
            campus_id: str UUID of the campus
            prefix: optional string prefix (e.g. 'GCQ')
            padding: zero-pad width (default 6)

        Returns:
            CampusIDConfig instance
        """
        from modules.campus_identity.models import CampusIDConfig
        config, created = CampusIDConfig.objects.get_or_create(
            campus_id=campus_id,
            defaults={'prefix': prefix, 'padding': padding, 'current_sequence': 0},
        )
        if not created:
            # Update prefix/padding but preserve sequence
            config.prefix = prefix
            config.padding = padding
            config.save(update_fields=['prefix', 'padding'])
        return config
