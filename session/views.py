from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render
from .models import Session
# Create your views here.

def session_list(request):
    sessions = Session.objects.all().order_by('-id')
    return render(request, 'session.html', {'sessions': sessions})

def session_detail(request, slug):
    session = get_object_or_404(Session, slug=slug)
    return render(request, 'session_detail.html', {'session': session})