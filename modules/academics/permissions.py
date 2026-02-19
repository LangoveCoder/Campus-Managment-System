"""
Academic Module Permissions
Constitution Section 5.2

Defines the permissions required for the Academic module.
"""

ACADEMIC_PERMISSIONS = [
    ('academics.view_program', 'View Academic Program', False),
    ('academics.create_program', 'Create Academic Program', False),
    ('academics.enroll_student', 'Enroll Student', False),
    ('academics.create_class_group', 'Create Class Group', False),
    ('academics.assign_teacher', 'Assign Teacher', False),
    ('academics.enter_assessment_result', 'Enter Assessment Result', False),
    ('academics.view_student_results', 'View Student Results', False),
    ('academics.modify_assessment_result', 'Modify Assessment Result', True),  # Dangerous
    ('academics.manage_programs', 'Manage Academic Programs', True),  # Dangerous
    ('academics.delete_enrollment', 'Delete Enrollment', True),  # Dangerous
]
