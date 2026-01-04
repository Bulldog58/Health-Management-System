from rest_framework import serializers
from .models import Patient, IssueSpecialtyMap
from hospitals.serializers import HospitalSerializer # Import the hospital serializer

# --- 1. IssueSpecialtyMap Serializer ---
class IssueSpecialtyMapSerializer(serializers.ModelSerializer):
    # Display the Specialty name instead of just the ID
    primary_specialty_name = serializers.CharField(source='primary_specialty.name', read_only=True)
    
    class Meta:
        model = IssueSpecialtyMap
        fields = ['id', 'issue_term', 'primary_specialty', 'primary_specialty_name']
 
# --- 2. Patient Serializer ---
class PatientSerializer(serializers.ModelSerializer):
    # Use the nested HospitalSerializer to display the assigned hospital details
    assigned_hospital_details = HospitalSerializer(source='assigned_hospital', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'age', 'health_issue', 'status', 
            'assigned_hospital', 'assigned_hospital_details', 'check_in_date'
        ]
        read_only_fields = ['check_in_date']