from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta
from kernel.models import Person, Campus, Role, UserRoleBinding

class TemporalConstraintTest(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            full_name="Test Person",
            primary_email="test@example.com",
            primary_phone="1234567890"
        )
        self.campus = Campus.objects.create(name="Test Campus")
        self.role = Role.objects.create(name="Test Role")
        self.now = timezone.now()

    def test_basic_binding(self):
        """Test creating a simple binding works."""
        validity = DateTimeTZRange(self.now, self.now + timedelta(hours=1))
        UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            validity=validity
        )
        self.assertEqual(UserRoleBinding.objects.count(), 1)

    def test_overlap_prevention(self):
        """Test that overlapping bindings are REJECTED."""
        # Binding 1: 10:00 - 12:00
        v1 = DateTimeTZRange(self.now, self.now + timedelta(hours=2), '[)')
        UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            validity=v1
        )
        
        # Binding 2: 11:00 - 13:00 (Overlaps!)
        v2 = DateTimeTZRange(self.now + timedelta(hours=1), self.now + timedelta(hours=3), '[)')
        
        with self.assertRaises(IntegrityError):
            UserRoleBinding.objects.create(
                person=self.person,
                role=self.role,
                campus=self.campus,
                validity=v2
            )

    def test_adjacent_allowed(self):
        """Test that adjacent bindings are ALLOWED."""
        # Binding 1: 10:00 - 11:00
        mid_point = self.now + timedelta(hours=1)
        v1 = DateTimeTZRange(self.now, mid_point, '[)')
        UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            validity=v1
        )
        
        # Binding 2: 11:00 - 12:00 (Starts exactly when prev ends)
        v2 = DateTimeTZRange(mid_point, self.now + timedelta(hours=2), '[)')
        UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            validity=v2
        )
        self.assertEqual(UserRoleBinding.objects.count(), 2)

    def test_different_roles_overlap_allowed(self):
        """Test that different roles can overlap."""
        role2 = Role.objects.create(name="Another Role")
        v = DateTimeTZRange(self.now, self.now + timedelta(hours=1), '[)')
        
        UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            validity=v
        )
        
        # Same time, different role -> OK
        UserRoleBinding.objects.create(
            person=self.person,
            role=role2,
            campus=self.campus,
            validity=v
        )
        self.assertEqual(UserRoleBinding.objects.count(), 2)

    def test_open_ended_overlap(self):
        """Test open-ended ranges overlap correctly."""
        # Binding 1: Now -> Forever
        v1 = DateTimeTZRange(self.now, None, '[)')
        UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus,
            validity=v1
        )
        
        # Binding 2: Tomorrow -> Tomorrow+1h (Overlaps because v1 is forever)
        v2 = DateTimeTZRange(self.now + timedelta(days=1), self.now + timedelta(days=1, hours=1), '[)')
        
        with self.assertRaises(IntegrityError):
            UserRoleBinding.objects.create(
                person=self.person,
                role=self.role,
                campus=self.campus,
                validity=v2
            )

    def test_default_validity(self):
        """Test that default validity is [now, infinity)."""
        binding = UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus
            # No validity provided
        )
        self.assertIsNotNone(binding.validity)
        self.assertIsNone(binding.validity.upper) # Infinite end
        # Start should be close to now
        self.assertTrue(abs(binding.validity.lower - timezone.now()) < timedelta(seconds=5))

    def test_deactivation_closes_range(self):
        """Test that setting is_active=False closes the validity range."""
        # Create open-ended binding
        binding = UserRoleBinding.objects.create(
            person=self.person,
            role=self.role,
            campus=self.campus
        )
        self.assertIsNone(binding.validity.upper)
        
        # Deactivate
        binding.is_active = False
        binding.save()
        
        # Reload and check is_currently_valid() — deactivation should invalidate the binding
        binding.refresh_from_db()
        self.assertFalse(binding.is_currently_valid())
