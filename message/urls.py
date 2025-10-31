from django.conf import settings
from django.conf.urls.static import static
from .views import session_list
from django.urls import path
from . import views

urlpatterns = [

path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('blogs/submit/', views.submit_blog, name='blog_submit'),
    path('blogs/manage/', views.pending_blogs, name='pending_blogs'),
    path('blogs/<int:pk>/approve/', views.approve_blog, name='approve_blog'),
    path('blogs/<int:pk>/reject/', views.reject_blog, name='reject_blog'),
    path('blogs/<int:pk>/delete/', views.delete_blog, name='delete_blog'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),

]