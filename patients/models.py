from django.db import models
from hospitals.models import Specialty, Hospital

class IssueSpecialtyMap(models.Model):
    issue_term = models.CharField(
        max_length=100,
        unique=True,
        help_text="e.g., 'Broken leg', 'Flu'"
    )
    primary_specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        related_name='mapped_issues'
    )

    class Meta:
        verbose_name = "Issue to Specialty Map"
        verbose_name_plural = "Issue to Specialty Maps"

    def __str__(self):
        return f"{self.issue_term} -> {self.primary_specialty.name}"

class Patient(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Assignment'),
        ('IN', 'Admitted (In-Patient)'),
        ('OUT', 'Discharged (Out-Patient)'),
    ]

    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    health_issue = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    # Changed related_name to avoid the collision error
    assigned_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients_app_records' 
    )
    check_in_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name