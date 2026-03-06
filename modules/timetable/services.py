from modules.timetable.models import TimetableSlot

DAY_ORDER = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']


class TimetableService:

    @staticmethod
    def get_weekly_timetable(class_group_id, campus_id):
        """Returns dict: {day: [slot, ...]} ordered by period."""
        slots = TimetableSlot.objects.filter(
            class_group_id=class_group_id,
            campus_id=campus_id,
        ).order_by('day', 'period')

        grid = {day: [] for day in DAY_ORDER}
        for slot in slots:
            if slot.day in grid:
                grid[slot.day].append(slot)
        return grid

    @staticmethod
    def get_all_slots(campus_id, class_group_id):
        return TimetableSlot.objects.filter(
            campus_id=campus_id,
            class_group_id=class_group_id,
        ).order_by('day', 'period')

    @staticmethod
    def create_slot(campus_id, class_group_id, day, period,
                    course_name, teacher_name='', room='',
                    start_time=None, end_time=None, room_fk_id=None):
        return TimetableSlot.objects.create(
            campus_id=campus_id,
            class_group_id=class_group_id,
            day=day,
            period=period,
            course_name=course_name,
            teacher_name=teacher_name,
            room=room,
            room_fk_id=room_fk_id,
            start_time=start_time,
            end_time=end_time,
        )

    @staticmethod
    def update_slot(slot_id, campus_id, **kwargs):
        updated = TimetableSlot.objects.filter(
            id=slot_id, campus_id=campus_id
        ).update(**kwargs)
        return updated > 0

    @staticmethod
    def delete_slot(slot_id, campus_id):
        deleted, _ = TimetableSlot.objects.filter(
            id=slot_id, campus_id=campus_id
        ).delete()
        return deleted > 0

    @staticmethod
    def get_slot(slot_id, campus_id):
        return TimetableSlot.objects.filter(
            id=slot_id, campus_id=campus_id
        ).first()

class RoomService:
    @staticmethod
    def get_rooms(campus_id):
        from modules.timetable.models import Room
        return Room.objects.filter(campus_id=campus_id, is_active=True).order_by('name')

    @staticmethod
    def create_room(campus_id, name, capacity=30, room_type='CLASSROOM'):
        from modules.timetable.models import Room
        return Room.objects.create(
            campus_id=campus_id,
            name=name,
            capacity=capacity,
            room_type=room_type
        )

    @staticmethod
    def delete_room(room_id, campus_id):
        from modules.timetable.models import Room
        from modules.timetable.models import TimetableSlot
        in_use = TimetableSlot.objects.filter(room_fk_id=room_id, campus_id=campus_id).exists()
        if in_use:
            raise ValueError("Room is assigned to existing slots. Remove those slots first.")
        Room.objects.filter(id=room_id, campus_id=campus_id).delete()
