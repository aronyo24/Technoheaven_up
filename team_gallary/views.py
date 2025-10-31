from django.shortcuts import render

from team_gallary.models import Gallery, Team
from django.shortcuts import get_object_or_404, redirect, render
# Create your views here.

def gallery(request):
    gallery = Gallery.objects.all()
    data = {'gallery': gallery}

    return render(request, 'gallery.html', data)

def team(request):
    team_members = Team.objects.all()
    data = {'team_members': team_members}
    return render(request, 'team.html', data)


def team_details(request, slug):
    team_member = get_object_or_404(Team, slug=slug)
    data = {'team_member': team_member}
    return render(request, 'team_m_de.html', data)
