from django.contrib.syndication.views import Feed
from blog.models import ArticlePage

class ArticleFeed(Feed):
    title = "Science News" # TODO: Update this with real information
    link = "/articles/"
    description = "Updates on science news."

    def items(self):
        return ArticlePage.objects.order_by('-date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.intro

    def item_link(self, item):
        return item.url