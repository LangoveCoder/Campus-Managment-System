from django.shortcuts import render, redirect
from modules.timetable.services import TimetableService
from modules.timetable.models import DAY_CHOICES, PERIOD_CHOICES


def _get_campus_id(request):
    campus_id = request.session.get('current_campus_id')
    return int(campus_id) if campus_id else None


def _get_person_id(request):
    person = getattr(request.user, 'person', None)
    return str(person.id) if person else None


def timetable_view(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    campus_id = _get_campus_id(request)
    if not campus_id:
        return redirect('/select-campus/')

    from modules.academics.services.academic_query_service import AcademicQueryService
    class_groups = list(AcademicQueryService.get_class_groups(campus_id))

    selected_id = request.GET.get('class_group_id')
    if not selected_id and class_groups:
        selected_id = str(class_groups[0].id)

    rows = []
    selected_group = None
    day_codes = [d[0] for d in DAY_CHOICES]
    period_codes = [p[0] for p in PERIOD_CHOICES]

    if selected_id:
        for cg in class_groups:
            if str(cg.id) == selected_id:
                selected_group = cg
                break

        raw = TimetableService.get_weekly_timetable(selected_id, campus_id)
        slot_map = {}
        for day, slots in raw.items():
            for slot in slots:
                slot_map[(day, slot.period)] = slot

        for p in period_codes:
            cells = [{'day': d, 'slot': slot_map.get((d, p))} for d in day_codes]
            rows.append({'period': p, 'cells': cells})

    can_manage = False
    person_id = _get_person_id(request)
    if person_id:
        try:
            from kernel.facades import AuthorizationFacade
            AuthorizationFacade.require(
                person_id=person_id,
                campus_id=campus_id,
                permission_code='timetable.manage_timetable'
            )
            can_manage = True
        except Exception:
            pass

    return render(request, 'timetable/timetable.html', {
        'active_section': 'timetable',
        'class_groups': class_groups,
        'selected_id': selected_id,
        'selected_group': selected_group,
        'rows': rows,
        'days': DAY_CHOICES,
        'can_manage': can_manage,
    })


def add_slot(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    campus_id = _get_campus_id(request)
    if not campus_id:
        return redirect('/select-campus/')

    person_id = _get_person_id(request)
    try:
        from kernel.facades import AuthorizationFacade
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='timetable.manage_timetable'
        )
    except Exception:
        return redirect('/timetable/')

    from modules.academics.services.academic_query_service import AcademicQueryService
    from modules.timetable.services import RoomService
    class_groups = list(AcademicQueryService.get_class_groups(campus_id))
    rooms = RoomService.get_rooms(campus_id)
    error = None

    if request.method == 'POST':
        try:
            room_fk_id_raw = request.POST.get('room_fk_id', '')
            room_fk_id = int(room_fk_id_raw) if room_fk_id_raw else None
            TimetableService.create_slot(
                campus_id=campus_id,
                class_group_id=request.POST['class_group_id'],
                day=request.POST['day'],
                period=request.POST['period'],
                course_name=request.POST['course_name'],
                teacher_name=request.POST.get('teacher_name', ''),
                room=request.POST.get('room', ''),
                room_fk_id=room_fk_id,
            )
            cg_id = request.POST['class_group_id']
            return redirect(f'/timetable/?class_group_id={cg_id}')
        except Exception as e:
            error = str(e)

    preselect = request.GET.get('class_group_id', '')
    return render(request, 'timetable/slot_form.html', {
        'active_section': 'timetable',
        'class_groups': class_groups,
        'rooms': rooms,
        'days': DAY_CHOICES,
        'periods': PERIOD_CHOICES,
        'preselect': preselect,
        'error': error,
        'action': 'Add',
    })


def delete_slot(request, slot_id):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    campus_id = _get_campus_id(request)
    if not campus_id:
        return redirect('/select-campus/')

    person_id = _get_person_id(request)
    try:
        from kernel.facades import AuthorizationFacade
        AuthorizationFacade.require(
            person_id=person_id,
            campus_id=campus_id,
            permission_code='timetable.manage_timetable'
        )
    except Exception:
        return redirect('/timetable/')

    if request.method == 'POST':
        slot = TimetableService.get_slot(slot_id, campus_id)
        cg_id = str(slot.class_group_id) if slot else ''
        TimetableService.delete_slot(slot_id, campus_id)
        return redirect(f'/timetable/?class_group_id={cg_id}')
    return redirect('/timetable/')


def rooms_view(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return redirect('/select-campus/')
    person_id = _get_person_id(request)
    try:
        from kernel.facades import AuthorizationFacade
        AuthorizationFacade.require(person_id, campus_id, 'timetable.manage_timetable')
    except Exception:
        return redirect('/timetable/')

    from modules.timetable.services import RoomService
    rooms = RoomService.get_rooms(campus_id)
    return render(request, 'timetable/rooms.html', {
        'active_section': 'timetable',
        'rooms': rooms,
    })


def add_room(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return redirect('/select-campus/')
    person_id = _get_person_id(request)
    try:
        from kernel.facades import AuthorizationFacade
        AuthorizationFacade.require(person_id, campus_id, 'timetable.manage_timetable')
    except Exception:
        return redirect('/timetable/')

    from modules.timetable.services import RoomService
    from modules.timetable.models import Room
    error = None

    if request.method == 'POST':
        try:
            RoomService.create_room(
                campus_id=campus_id,
                name=request.POST['name'],
                capacity=int(request.POST.get('capacity', 30)),
                room_type=request.POST.get('room_type', 'CLASSROOM'),
            )
            return redirect('/timetable/rooms/')
        except Exception as e:
            error = str(e)

    room_types = Room._meta.get_field('room_type').choices
    return render(request, 'timetable/room_form.html', {
        'active_section': 'timetable',
        'room_types': room_types,
        'error': error,
    })


def delete_room(request, room_id):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    campus_id = request.session.get('current_campus_id')
    if not campus_id:
        return redirect('/select-campus/')
    person_id = _get_person_id(request)
    try:
        from kernel.facades import AuthorizationFacade
        AuthorizationFacade.require(person_id, campus_id, 'timetable.manage_timetable')
    except Exception:
        return redirect('/timetable/')

    if request.method == 'POST':
        from modules.timetable.services import RoomService
        RoomService.delete_room(room_id, campus_id)
    return redirect('/timetable/rooms/')
