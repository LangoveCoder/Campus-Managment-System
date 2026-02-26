"""
Academics Module URL Configuration
Prefix: api/academics/ (wired in config/urls.py)
"""
from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # -----------------------------------------------------------------------
    # Program → Cycle → Class hierarchy (3 GAPs — service methods missing)
    # -----------------------------------------------------------------------
    path('programs/',
         views.ProgramListView.as_view(),
         name='program_list'),

    path('programs/<int:program_id>/cycles/',
         views.ProgramCyclesView.as_view(),
         name='program_cycles'),

    path('cycles/<int:cycle_id>/classes/',
         views.CycleClassesView.as_view(),
         name='cycle_classes'),

    # -----------------------------------------------------------------------
    # Class queries (LIVE)
    # -----------------------------------------------------------------------
    path('classes/<int:class_group_id>/students/',
         views.ClassStudentsView.as_view(),
         name='class_students'),

    path('classes/<int:class_group_id>/teachers/',
         views.ClassTeachersView.as_view(),
         name='class_teachers'),

    path('classes/<int:class_group_id>/courses/',
         views.ClassCoursesView.as_view(),
         name='class_courses'),

    path('classes/<int:class_group_id>/results/',
         views.ClassResultsSummaryView.as_view(),
         name='class_results'),

    # -----------------------------------------------------------------------
    # Enrollment (create LIVE, detail GAP)
    # -----------------------------------------------------------------------
    path('enroll/',
         views.EnrollView.as_view(),
         name='enroll'),

    path('enrollments/<int:enrollment_id>/',
         views.EnrollmentDetailView.as_view(),
         name='enrollment_detail'),

    # -----------------------------------------------------------------------
    # Assessments (LIVE)
    # -----------------------------------------------------------------------
    path('assessments/create/',
         views.AssessmentCreateView.as_view(),
         name='assessment_create'),

    path('assessments/<int:instance_id>/results/',
         views.AssessmentResultEntryView.as_view(),
         name='assessment_results'),
]
