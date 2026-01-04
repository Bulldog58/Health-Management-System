from django.shortcuts import render
from django.db.models import Count, Q, F  # Added F here
from django.db import models              # Added models import
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from .models import Hospital, Specialty 
from .serializers import HospitalSerializer, SpecialtySerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # Add this import
from django.db.models import Q 
import json

# --- Template View for Frontend ---

def dashboard(request):
    query = request.GET.get('search')
    hospitals = Hospital.objects.all()
    
    if query:
        hospitals = hospitals.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )

    specialties = Specialty.objects.all()
    
    # Data for the Chart (Feature 1)
    # This creates a list of labels and counts for the chart
    chart_labels = [s.name for s in specialties]
    chart_data = [Hospital.objects.filter(specialties=s).count() for s in specialties]

    context = {
        'hospitals': hospitals,
        'specialties': specialties,
        'hosp_count': hospitals.count(),
        'spec_count': specialties.count(),
        'total_capacity': sum(h.total_capacity for h in hospitals),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'hospitals/index.html', context)

# --- API ViewSet for Hospital Management ---

class HospitalViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Hospitals.
    Includes filtering by name and address.
    """
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['address', 'name']

# --- Specialized Recommendation Logic ---

class RecommendationView(generics.ListAPIView):
    """
    The Core Recommendation Engine.
    Usage: /api/recommend/?issue=cardiology
    """
    serializer_class = HospitalSerializer

    def get_queryset(self):
        issue_query = self.request.query_params.get('issue', None)
        if not issue_query:
            return Hospital.objects.none()

        # 1. Annotate with patient count for efficient filtering
        # 2. Filter by specialty name and available capacity
        # 3. Sort by the most available space (least crowded)
        queryset = Hospital.objects.annotate(
            active_patients=Count('patients', filter=Q(patients__status='IN'))
        ).filter(
            specialties__name__icontains=issue_query,
            active_patients__lt=models.F('total_capacity')
        ).order_by('active_patients')

        return queryset[:3]
        # --- Specialty ViewSet (The missing piece!) ---
class SpecialtyViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Medical Specialties.
    """
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

def delete_hospital(request, pk):
    # Find the hospital or return a 404 error if it doesn't exist
    hospital = get_object_or_404(Hospital, pk=pk)
    
    if request.method == 'POST':
        hospital.delete()
        return redirect('dashboard') # Refresh the dashboard
        
    return redirect('dashboard') # Fallback    