from django.test import TestCase
from kernel.models import Person, Campus
from modules.profiles.models import PersonProfile
from modules.profiles.services import get_or_create_profile, update_profile, get_profile


class PersonProfileTests(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(name="Test Campus", campus_type="PHYSICAL")
        self.person = Person.objects.create(
            full_name="Dr. Tariq Mehmood",
            primary_email="tariq@example.com",
        )

    def test_get_or_create_creates_profile(self):
        """Creating a profile for a new person+campus should succeed."""
        profile = get_or_create_profile(self.person.id, self.campus.id)
        self.assertIsInstance(profile, PersonProfile)
        self.assertEqual(profile.person, self.person)
        self.assertEqual(profile.campus, self.campus)

    def test_get_or_create_is_idempotent(self):
        """Calling get_or_create twice should return the same profile."""
        p1 = get_or_create_profile(self.person.id, self.campus.id)
        p2 = get_or_create_profile(self.person.id, self.campus.id)
        self.assertEqual(p1.id, p2.id)
        self.assertEqual(PersonProfile.objects.filter(person=self.person, campus=self.campus).count(), 1)

    def test_update_profile_fields(self):
        """update_profile should persist the provided fields."""
        update_profile(self.person.id, self.campus.id, {
            'blood_group': 'O+',
            'cnic': '35202-1234567-1',
            'father_name': 'Mehmood Khan',
            'qualification': 'PhD Computer Science',
        })
        profile = get_profile(self.person.id, self.campus.id)
        self.assertEqual(profile.blood_group, 'O+')
        self.assertEqual(profile.cnic, '35202-1234567-1')
        self.assertEqual(profile.father_name, 'Mehmood Khan')
        self.assertEqual(profile.qualification, 'PhD Computer Science')

    def test_empty_string_stored_as_none(self):
        """Empty string values should be stored as NULL, not empty strings."""
        update_profile(self.person.id, self.campus.id, {'blood_group': ''})
        profile = get_profile(self.person.id, self.campus.id)
        self.assertIsNone(profile.blood_group)

    def test_unique_together_constraint(self):
        """Two profiles for the same person+campus should raise an IntegrityError."""
        from django.db import IntegrityError
        get_or_create_profile(self.person.id, self.campus.id)
        with self.assertRaises(IntegrityError):
            PersonProfile.objects.create(person=self.person, campus=self.campus)

    def test_get_profile_returns_none_if_missing(self):
        """get_profile should return None if no profile exists."""
        result = get_profile(self.person.id, self.campus.id)
        self.assertIsNone(result)

    def test_str_representation(self):
        """__str__ should include the person's full name."""
        profile = get_or_create_profile(self.person.id, self.campus.id)
        self.assertIn("Dr. Tariq Mehmood", str(profile))
