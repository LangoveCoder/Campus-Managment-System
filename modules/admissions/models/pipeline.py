
from django.db import models
from django.utils.translation import gettext_lazy as _
from kernel.models.base import BaseCampusModel

class Applicant(BaseCampusModel):
    """
    Represents a human BEFORE they become a student.
    Minimal identity data.
    """
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=50, blank=True, null=True)
    
    # Contact Info (JSON) - Email, Phone, Address
    # Structure not enforced by backend.
    contact_info = models.JSONField(default=dict)
    
    # Guardian Info (JSON) - Father/Guardian Name, CNIC, Occupation
    # Structure not enforced by backend.
    guardian_info = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.date_of_birth})"

class AdmissionApplication(BaseCampusModel):
    """
    The specific application instance (Pipeline Object).
    Holds the dynamic form payload.
    """
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', _('Submitted')
        TESTED = 'TESTED', _('Tested')
        INTERVIEWED = 'INTERVIEWED', _('Interviewed')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        WAITLISTED = 'WAITLISTED', _('Waitlisted')

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications')
    
    # Optional link to an Academic Program (target of admission)
    # References module.academics.AcademicProgram but via lazy string or integer ID if loose coupling preferred.
    # For strict FK: 'academics.AcademicProgram'
    academic_program = models.ForeignKey('academics.AcademicProgram', on_delete=models.SET_NULL, null=True, blank=True)
    
    # The Form Data (OPAQUE)
    # Backend does NOT validate this. UI/Evaluators interpret it.
    form_payload = models.JSONField(default=dict)
    
    # Schema Versioning (e.g., 'v1-metric', 'v2-olevel')
    form_schema_version = models.CharField(max_length=50, default='v1')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"App-{self.id}: {self.applicant.full_name} ({self.status})"

class AdmissionTestResult(BaseCampusModel):
    """
    Result of a testing service (external or internal).
    """
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='test_results')
    score = models.FloatField()
    total_score = models.FloatField(default=100.0)
    
    # Percentile or Rank (optional)
    percentile = models.FloatField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    
    # Source of request (e.g., 'NTS', 'Internal', 'GAT')
    source = models.CharField(max_length=100, default='Internal')
    
    conducted_at = models.DateTimeField(auto_now_add=True)

class InterviewEvaluation(BaseCampusModel):
    """
    Log of an interview conducted by a staff member.
    """
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey('kernel.Person', on_delete=models.PROTECT, related_name='conducted_interviews')
    
    remarks = models.TextField()
    recommendation = models.CharField(max_length=50) # e.g., "Highly Recommended", "Hold"
    
    conducted_at = models.DateTimeField(auto_now_add=True)

class AdmissionDecision(BaseCampusModel):
    """
    Final verdict on an application.
    """
    class Verdict(models.TextChoices):
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        WAITLISTED = 'WAITLISTED', _('Waitlisted')

    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='decisions')
    decision = models.CharField(max_length=20, choices=Verdict.choices)
    
    decided_by = models.ForeignKey('kernel.Person', on_delete=models.PROTECT)
    decided_at = models.DateTimeField(auto_now_add=True)
    
    comments = models.TextField(blank=True)
