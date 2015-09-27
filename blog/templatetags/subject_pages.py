from django import template
from blog.models import Subject, ArticleIndexPage
import sys
from collections import OrderedDict

register = template.Library()

@register.assignment_tag(name='subject_pages')
def subject_pages():
    pages = {}
    for s in Subject.objects.all():
        pages[s.subject_name] = ArticleIndexPage.objects.filter(subject=s)[0].url
    pages = OrderedDict(sorted(pages.items()))
    return pages