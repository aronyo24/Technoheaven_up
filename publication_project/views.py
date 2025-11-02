
from django.shortcuts import render

from .models import Project, Publication, Resource, Service, Client
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.

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

def services(request):
    # load services and group them by category (preserves defined order)
    services_qs = Service.objects.all()
    categories = []
    for value, label in Service.SERVICE_CATEGORIES:
        categories.append({
            'value': value,
            'label': label,
            'services': services_qs.filter(category=value)
        })

    return render(request, 'services.html', {'categories': categories})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    return render(request, 'services_de.html', {'service': service})


def clients(request):
    clients = Client.objects.all()
    return render(request, 'clients.html', {'clients': clients})
