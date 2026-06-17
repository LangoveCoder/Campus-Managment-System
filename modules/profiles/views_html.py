from django.shortcuts import render, redirect
from kernel.models import Person

def _get_person_id(request):
    return request.session.get('person_id')

def edit_profile(request, person_id):
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return redirect('select_campus')

    from modules.profiles.services import get_or_create_profile, update_profile
    from modules.profiles.models import BLOOD_GROUP_CHOICES

    try:
        person = Person.objects.get(id=person_id)
    except Person.DoesNotExist:
        return redirect('dashboard:home')

    profile = get_or_create_profile(person_id=person_id, campus_id=campus_id)
    error = None
    success = None

    if request.method == 'POST':
        try:
            data = {
                'date_of_birth': request.POST.get('date_of_birth') or None,
                'blood_group': request.POST.get('blood_group') or None,
                'cnic': request.POST.get('cnic') or None,
                'phone': request.POST.get('phone') or None,
                'address': request.POST.get('address') or None,
                'father_name': request.POST.get('father_name') or None,
                'mother_name': request.POST.get('mother_name') or None,
                'guardian_name': request.POST.get('guardian_name') or None,
                'guardian_phone': request.POST.get('guardian_phone') or None,
                'guardian_relation': request.POST.get('guardian_relation') or None,
                'emergency_contact_name': request.POST.get('emergency_contact_name') or None,
                'emergency_contact_phone': request.POST.get('emergency_contact_phone') or None,
                'previous_institution': request.POST.get('previous_institution') or None,
                'qualification': request.POST.get('qualification') or None,
                'specialization': request.POST.get('specialization') or None,
                'join_date': request.POST.get('join_date') or None,
            }
            update_profile(person_id=person_id, campus_id=campus_id, data=data)
            success = 'Profile updated successfully.'
            profile = get_or_create_profile(person_id=person_id, campus_id=campus_id)
        except Exception as e:
            error = str(e)

    return render(request, 'profiles/edit_profile.html', {
        'person': person,
        'profile': profile,
        'blood_group_choices': BLOOD_GROUP_CHOICES,
        'error': error,
        'success': success,
        'active_section': 'profiles',
    })
