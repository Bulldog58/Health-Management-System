from django.db import models
from django.utils import timezone

class Specialty(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="e.g., Orthopedics, Cardiology, General Surgery"
    )

    class Meta:
        verbose_name_plural = "Specialties"
        ordering = ['name']

    def __str__(self):
        return self.name

class Hospital(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    total_capacity = models.IntegerField(
        help_text="Maximum number of patients the hospital can admit."
    )
    specialties = models.ManyToManyField(
        Specialty,
        related_name='hospitals',
        help_text="Select all specialties offered by this hospital."
    )

    def __str__(self):
        return f"{self.name} ({self.address})"

    @property
    def current_occupancy(self):
        # Updated to match the unique related_name below
        return self.hospitals_patients.filter(status='IN').count()

class Patient(models.Model):
    STATUS_CHOICES = [('IN', 'Inpatient'), ('OUT', 'Outpatient')]
    
    name = models.CharField(max_length=200)
    hospital = models.ForeignKey(
        Hospital, 
        on_delete=models.CASCADE, 
        related_name='hospitals_patients' # Unique ID for this app
    )
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='OUT')
    admitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"{self.patient.name} - {self.appointment_date}"