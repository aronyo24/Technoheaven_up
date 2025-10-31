from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404
from django.contrib import messages     
from .models import Blog, Comment

def blog_list(request):
    selected = request.GET.get('category')
    search = request.GET.get('search', '').strip()

    qs = Blog.objects.filter(status='published').order_by('-date', '-pk')
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
    if selected:
        qs = qs.filter(category=selected)

    # simple color list that will be reused/cycled for categories
    color_palette = ['#007bff', '#6610f2', '#20c997', '#e83e8c', '#fd7e14', '#17a2b8', '#6f42c1', '#20a8d8', '#343a40']

    # get choices from the Blog model and attach a color and count to each
    raw_categories = Blog._meta.get_field('category').choices
    categories = []
    for i, (value, label) in enumerate(raw_categories):
        published_count = Blog.objects.filter(status='published', category=value).count()
        categories.append({
            'value': value,
            'label': label,
            'color': color_palette[i % len(color_palette)],
            'count': published_count
        })

    # paginate (6 posts per page)
    paginator = Paginator(qs, 6)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # preserve other GET params except page
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')
    querystring_base = params.urlencode()  # may be empty

    data = {
        'blogs': qs,  # kept for backward compat if used elsewhere
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'search': search,
        'all_blogs': Blog.objects.filter(status='published'),
        'categories': categories,
        'selected_category': selected,
        'querystring_base': querystring_base,
        'show_submit_callout': True,
    }
    return render(request, 'blog.html', data)


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    is_owner = request.user.is_authenticated and blog.submitted_by_id == request.user.id
    can_moderate = request.user.is_authenticated and request.user.is_staff

    if blog.status != 'published' and not (is_owner or can_moderate):
        raise Http404("This blog post is not available.")

    if request.method == "POST":
        if request.POST.get('like') and blog.status == 'published':
            blog.likes = (blog.likes or 0) + 1
            blog.save(update_fields=['likes'])
            return redirect('blog_detail', slug=blog.slug)

        name = request.POST.get('name', '').strip()
        comment_text = request.POST.get('comment', '').strip()
        if name and comment_text:
            Comment.objects.create(blog=blog, name=name, comment=comment_text)
            messages.success(request, "Thanks for sharing your thoughts!")
            return redirect('blog_detail', slug=blog.slug)

    comments = Comment.objects.filter(blog=blog).order_by('-date')

    color_palette = ['#007bff', '#6610f2', '#20c997', '#e83e8c', '#fd7e14', '#17a2b8', '#6f42c1', '#20a8d8', '#343a40']
    raw_categories = Blog._meta.get_field('category').choices
    categories = []
    for i, (value, label) in enumerate(raw_categories):
        categories.append({
            'value': value,
            'label': label,
            'color': color_palette[i % len(color_palette)],
            'count': Blog.objects.filter(status='published', category=value).count()
        })

    selected = request.GET.get('category')

    prev_blog = Blog.objects.filter(
        status='published'
    ).filter(
        Q(date__lt=blog.date) | (Q(date=blog.date) & Q(pk__lt=blog.pk))
    ).order_by('-date', '-pk').first()
    next_blog = Blog.objects.filter(
        status='published'
    ).filter(
        Q(date__gt=blog.date) | (Q(date=blog.date) & Q(pk__gt=blog.pk))
    ).order_by('date', 'pk').first()

    context = {
        'blog': blog,
        'comments': comments,
        'all_blogs': Blog.objects.filter(status='published'),
        'categories': categories,
        'selected_category': selected,
        'prev_blog': prev_blog,
        'next_blog': next_blog,
        'is_owner': is_owner,
        'can_moderate': can_moderate,
    }
    return render(request, 'blogs_de.html', context)


