from django.shortcuts import render, get_object_or_404

from message.models import News
from publication_project.models import Publication, Project, Resource
from team_gallary.models import Team, Gallery


# Create your views here.
def home(request):
    news = News.objects.all()
    publications = Publication.objects.all().order_by('-id')
    data = {'publications': publications,
            'news': news
            }

    return render(request, 'index.html', data)


def gallery(request):
    gallery = Gallery.objects.all()
    data = {'gallery': gallery}

    return render(request, 'gallary.html', data)


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def projects(request):
    projects = Project.objects.all()
    data = {'projects': projects}
    return render(request, 'project.html', data)


def publications(request):
    publications = Publication.objects.all().order_by('-id')
    data = {'publications': publications}

    return render(request, 'publications.html', data)


def research(request):
    return render(request, 'research.html')


def resources(request):
    resources = Resource.objects.all()
    data = {'resources': resources}
    return render(request, 'resources.html', data)


def resources_details(request, slug):
    resource = get_object_or_404(Resource, slug=slug)
    data = {'resource': resource}
    return render(request, 'resources_de.html', data)


def team(request):
    team_members = Team.objects.all()
    data = {'team_members': team_members}
    return render(request, 'team.html', data)


def team_details(request, slug):
    team_member = get_object_or_404(Team, slug=slug)
    data = {'team_member': team_member}
    return render(request, 'team_m_de.html', data)
