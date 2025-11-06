from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/blog/new/', views.submit_blog, name='submit_blog'),
    path('dashboard/blog/<slug:slug>/edit/', views.edit_blog, name='edit_blog'),
    path('dashboard/profile/', views.edit_profile, name='edit_profile'),
    path('dashboard/security/', views.change_password, name='change_password'),
    
 


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
