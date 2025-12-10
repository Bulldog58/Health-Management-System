
_**🏥 Hospital Resource & Patient Management System (HRMS)**_
This project implements a backend API for a smart hospital resource management and patient assignment system. The core feature is a Recommendation Engine that intelligently suggests the best hospital for a patient based on their health issue, required specialty, and real-time hospital capacity.

_🌟 Key Features_
RESTful API: Built using Django and Django Rest Framework (DRF).

Intelligent Routing: Core recommendation logic ranks hospitals based on specialty match (priority) and capacity utilization (tie-breaker/secondary factor).

Real-time Metrics: Hospitals display dynamic current_occupancy and the central Dashboard provides aggregated, real-time metrics.

Configurable Data: Patient issues are mapped to standard specialties via the IssueSpecialtyMap model, allowing easy data management via the Django Admin.

_🚀 Setup and Installation_
These instructions assume you have Python 3.x and pip installed.

**1. Project Initialization**
Bash

# Clone the repository (or navigate to the hrms_project folder)
cd hrms_project

# Install required packages
pip install django djangorestframework

# Note: If 'python' command fails, use the full path: 
# C:\Users\fello\AppData\Local\Programs\Python\Python314\python.exe

# Run migrations to set up the database schema
python manage.py migrate

**2. Create Admin User & Seed Data**
You must create a superuser to access the Django Admin and enter the necessary seed data for the Recommendation Engine (Specialties, Hospitals, and Issue Mappings).

Bash

# Create superuser credentials
python manage.py createsuperuser

# Start the development server
python manage.py runserver
Open your browser to http://127.0.0.1:8000/admin/ and log in.

**3. Essential Seed Data**
For the API to function, you must manually create the following via the Admin interface:
 Specialties: Create Orthopedics, Cardiology, Neurology, etc.
 Hospitals: Create 2-3 hospitals and assign them the specialties they offer.
 Issue to Specialty Maps: Create mappings (e.g., Broken Leg $\rightarrow$ Orthopedics, Chest Pain $\rightarrow$ Cardiology).

**📋 API Endpoints Reference**
All API endpoints are prefixed with /api/v1/.
CategoryMethodEndpointDescriptionHospitalsGET / POST/api/v1/hospitals/List all hospitals (with occupancy) or create a new one.SpecialtiesGET / POST/api/v1/specialties/List or manage standard medical specialties.PatientsGET / POST/api/v1/patients/List all patients or register a new patient (status=PENDING).AssignmentPATCH / PUT/api/v1/patients/{id}/assign/Assigns a patient to a hospital (requires hospital_id in body).RecommendationGET/api/v1/recommend/{issue_term}/CORE LOGIC: Get top 3 hospital recommendations.DashboardGET/api/v1/dashboard/Provides aggregated metrics (capacity, admitted patients).

**💡 Core Logic Deep Dive**
**1. Hospital Recommendation

The core logic is implemented in the HospitalRecommendationView (/api/v1/recommend/). It follows this three-step process:

*Specialty Mapping: The input patient_issue (e.g., "Severe Headache") is matched to a standardized Specialty using the IssueSpecialtyMap model.

*Filtering: Filters the entire hospital list down to only those that offer the required specialty.

*Scoring & Ranking: Remaining hospitals are scored based on the formula:

$$\text{Score} = 100 + \left( \frac{\text{Capacity} - \text{Occupancy}}{\text{Capacity}} \times 50 \right)$$
-This ensures that specialty match has priority (base score 100), and the remaining capacity acts as a secondary reward system to promote load balancing. The top 3 hospitals are returned.


**🛠️ Testing Example**
To test the entire workflow, follow these steps:

**1.Register a Patient (POST)**

*URL: http://127.0.0.1:8000/api/v1/patients/

*Body: {"name": "Jane Doe", "age": 30, "health_issue": "Broken Leg"}

*Result: Patient ID is returned (e.g., 10).

**2.Get Recommendation (GET)**

*URL: http://127.0.0.1:8000/api/v1/recommend/Broken%20Leg/

*Result: A list of hospitals specializing in Orthopedics, ranked by score.

    **2. Real-Time Occupancy**
The Hospital model uses a dynamic @property method (current_occupancy) to calculate the number of admitted patients by querying the Patient model. This ensures occupancy is always calculated on the fly without database redundancy.

Python

# hospitals/models.py (Snippet)
@property
def current_occupancy(self):
    return self.patient_set.filter(status='IN').count()
**3.Assign Patient (PATCH) (Assume the top hospital has ID 2)**

*URL: http://127.0.0.1:8000/api/v1/patients/10/assign/

*Body: {"hospital_id": 2}

*Result: Patient status changes to 'IN', check-in date is set, and Hospital 2's occupancy increases.


