from django.conf import settings
from django.conf.urls.static import static
from .views import session_list
from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('contact/', views.contact, name='contact'),
    path('projects/', views.projects, name='projects'),
    path('publications/', views.publications, name='publications'),
    path('research/', views.research, name='research'),
    path('resources/', views.resources, name='resources'),
    path('resources/<slug:slug>/', views.resources_details, name='resources_details'),
    path('team/', views.team, name='team'),
    path('team/member/<slug:slug>/', views.team_details, name='team_details'),
    path('sessions/', session_list, name='session_list'),
    path('clients/', views.clients, name='clients'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('blogs/submit/', views.submit_blog, name='submit_blog'),
    path('blogs/<int:pk>/delete/', views.delete_blog, name='delete_blog'),
    path('blogs/pending/', views.pending_blogs, name='pending_blogs'),
    path('blogs/<int:pk>/approve/', views.approve_blog, name='approve_blog'),
    path('blogs/<int:pk>/reject/', views.reject_blog, name='reject_blog'),
    


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
