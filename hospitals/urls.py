# hrms_project/hospitals/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import dashboard

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'hospitals', views.HospitalViewSet)
router.register(r'specialties', views.SpecialtyViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard, name='dashboard'),
    # This route takes the ID (pk) of the hospital you want to delete
    path('hospital/<int:pk>/delete/', views.delete_hospital, name='delete_hospital'),
]