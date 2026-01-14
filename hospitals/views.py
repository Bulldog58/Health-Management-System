from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, F
from django.db import models
from django.utils import timezone
from django.contrib import messages
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from itertools import chain # Used to merge patient lists
import json

# Import models from BOTH apps
from .models import Hospital, Specialty, Patient as HospPatient, Appointment 
from patients.models import Patient as PatPatient
from .serializers import HospitalSerializer, SpecialtySerializer

# --- 1. THE UNIFIED DASHBOARD VIEW ---
def dashboard(request):
    query = request.GET.get('search')
    hospitals = Hospital.objects.all()
    
    # Search Logic
    if query:
        hospitals = hospitals.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )

    specialties = Specialty.objects.all()
    
    # Fetch Top 5 Patients from both models
    h_patients = HospPatient.objects.all().order_by('-id')[:5]
    p_patients = PatPatient.objects.all().order_by('-id')[:5]
    # Merge them into one list for the table
    combined_patients = list(chain(h_patients, p_patients))

    # Stats Calculations
    pending_count = Appointment.objects.filter(
        status='scheduled', 
        appointment_date__gte=timezone.now()
    ).count()
    
    # Calculate global capacity
    total_cap = sum(h.total_capacity for h in hospitals)

    # Chart.js Data
    chart_labels = [s.name for s in specialties]
    chart_data = [Hospital.objects.filter(specialties=s).count() for s in specialties]

    context = {
        'hospitals': hospitals,
        'specialties': specialties,
        'combined_patients': combined_patients, # Used in the table
        'pending_count': pending_count,
        'hosp_count': hospitals.count(),
        'spec_count': specialties.count(),
        'total_capacity': total_cap,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'hospitals/index.html', context)

# --- 2. API VIEWSETS (Needed for your URLs) ---

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['address', 'name']

class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

class RecommendationView(generics.ListAPIView):
    serializer_class = HospitalSerializer

    def get_queryset(self):
        issue_query = self.request.query_params.get('issue', None)
        if not issue_query:
            return Hospital.objects.none()

        # Filters by combining occupancy across both patient sources
        queryset = Hospital.objects.annotate(
            active_h = Count('hospitals_patients', filter=Q(hospitals_patients__status='IN')),
            active_p = Count('patients_app_records', filter=Q(patients_app_records__status='IN'))
        ).filter(
            specialties__name__icontains=issue_query,
            active_h__lt=F('total_capacity') # Simplified check
        ).order_by('active_h')

        return queryset[:3]

def delete_hospital(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        hospital.delete()
        messages.success(request, "Hospital deleted successfully.")
    return redirect('dashboard')