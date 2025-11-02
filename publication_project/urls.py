from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('projects/', views.projects, name='projects'),
    path('publications/', views.publications, name='publications'),
    path('research/', views.research, name='research'),
    path('resources/', views.resources, name='resources'),
    path('resources/<slug:slug>/', views.resources_details, name='resources_details'),
    path('clients/', views.clients, name='clients'),
    


]

