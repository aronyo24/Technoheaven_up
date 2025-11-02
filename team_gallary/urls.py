from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [

    
    path('gallery/', views.gallery, name='gallery'),
    path('team/', views.team, name='team'),
    path('team/member/<slug:slug>/', views.team_details, name='team_details'),
  
    
 


]
