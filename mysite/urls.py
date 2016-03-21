from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
import search.views

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls
from blog.feeds import ArticleFeed

from wiki.urls import get_pattern as get_wiki_pattern
from django_nyt.urls import get_pattern as get_nyt_pattern


urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    # Search/filter articles
    url(r'^search/$', search.views.search, name='search'),
    url(r'^network/$', search.views.articles_network, name='network'),
    url(r'^explore/$', search.views.articles_filter, name='explore'),
    # JSON views (for search/filter articles)
    url(r'^get-articles/$', search.views.get_articles, name='get_articles'),
    url(r'^get-subject-network/$', search.views.get_subject_network, name='get_subject_network'),

    url(r'^feed/$', ArticleFeed(), name='feed'),

    # Django wiki
    url(r'^notifications/', get_nyt_pattern()),
    url(r'^wiki/', get_wiki_pattern()),

    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic import TemplateView

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
