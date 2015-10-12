from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.template.loader import render_to_string

import json
import sys

from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch.models import Query

from blog.models import ArticlePage, SubjectSnippet, SubjectPanelField
from images.models import CustomImage


def search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        search_results = Page.objects.live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })


def articles_network(request):
    return render(request, 'search/articles_network.html')


def articles_filter(request):
    # List of all subjects
    subject_names = SubjectSnippet.objects.values_list('subject_name', flat=True).order_by('subject_name')
    return render(request, 'search/articles_filter.html', {
        'subject_names': subject_names
    })


def get_articles(request):
    if request.method == 'GET':
        search_text = request.GET.get('search_text')
        subjects = search_text.split(', ')
        articles = ArticlePage.objects.live()
        for s in subjects:
            if SubjectSnippet.objects.filter(subject_name=s).exists():
                articles = articles.filter(subjects__subject__subject_name=s)
        html = render_to_string('search/preview_articles.html', {'articles': articles})
        return HttpResponse(html)
    else:
        pass


def get_subject_network(request):
    '''
    Get all of the data about the network of subjects to put into the vis.js network
    '''
    subjects = SubjectSnippet.objects.all()
    nodes = []
    edges = []
    subjects_unused = subjects
    for s in subjects:
        articles_this_subject = ArticlePage.objects.filter(subjects__subject=s)
        # Get nodes
        nodes.append({
            'id': s.subject_name,
            'label': s.subject_name,
            'value': articles_this_subject.count()
        })
        # Get edges
        subjects_unused = subjects_unused.exclude(pk=s.pk)
        for s2 in subjects_unused:
            article_count_subjs = articles_this_subject.filter(subjects__subject=s2).count()
            if article_count_subjs > 0:
                edges.append({
                    'id': s.subject_name + ', ' + s2.subject_name,
                    'from': s.subject_name,
                    'to': s2.subject_name,
                    'value': article_count_subjs
                })

    return HttpResponse(
        json.dumps({
            'nodes': nodes,
            'edges': edges}),
        content_type='application/json'
    )