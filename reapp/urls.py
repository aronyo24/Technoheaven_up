from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('projects/', views.projects, name='projects'),
    path('publications/', views.publications, name='publications'),
    path('research/', views.research, name='research'),
    path('resources/', views.resources, name='resources'),
    path('resources/<slug:slug>/', views.resources_details, name='resources_details'),
    path('team/', views.team, name='team'),
    path('team/member/<slug:slug>/', views.team_details, name='team_details'),



]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
