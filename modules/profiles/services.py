from modules.profiles.models import PersonProfile

def get_or_create_profile(person_id, campus_id):
    profile, _ = PersonProfile.objects.get_or_create(
        person_id=person_id,
        campus_id=campus_id,
    )
    return profile

def update_profile(person_id, campus_id, data: dict):
    profile = get_or_create_profile(person_id, campus_id)
    allowed = [
        'date_of_birth', 'blood_group', 'cnic', 'phone', 'address',
        'father_name', 'mother_name', 'guardian_name', 'guardian_phone',
        'guardian_relation', 'emergency_contact_name', 'emergency_contact_phone',
        'previous_institution', 'qualification', 'specialization', 'join_date',
    ]
    for field in allowed:
        if field in data:
            setattr(profile, field, data[field] or None)
    profile.save()
    return profile

def get_profile(person_id, campus_id):
    try:
        return PersonProfile.objects.get(person_id=person_id, campus_id=campus_id)
    except PersonProfile.DoesNotExist:
        return None
