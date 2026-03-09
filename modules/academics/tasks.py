from celery import shared_task

@shared_task(name='academics.bulk_enrollment')
def bulk_enrollment(campus_id, class_group_id, student_ids):
    """Process bulk enrollment async."""
    from modules.academics.services import EnrollmentService
    results = {'success': [], 'failed': []}
    for student_id in student_ids:
        try:
            EnrollmentService.enroll_student(campus_id, class_group_id, student_id)
            results['success'].append(student_id)
        except Exception as e:
            results['failed'].append({'id': student_id, 'error': str(e)})
    return results
