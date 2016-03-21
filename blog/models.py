from django.db import models
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel,
                                                MultiFieldPanel,
                                                PageChooserPanel,
                                                StreamFieldPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailcore import blocks
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel


@register_snippet
class SubjectSnippet(models.Model):
    """
    Identifies the different subjects under which to categorize articles
    """
    subject_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.subject_name


@register_snippet
class AuthorSnippet(models.Model):
    """
    Create a profile for each author, which will be paired with the articles they write
    """
    # NOT USED NOW
    author_name = models.CharField(max_length=255)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL)
    portrait = models.ForeignKey(
        'images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    bio = models.TextField(max_length=800, null=True)
    homepage = models.URLField(blank=True)

    panels = [
        FieldPanel('author_name'),
        FieldPanel('user'),
        FieldPanel('bio'),
        ImageChooserPanel('portrait'),
        FieldPanel('homepage'),
    ]

    def __unicode__(self):
        return self.author_name

    class Meta:
        verbose_name = "Author"


class CaptionedImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(help_text='This will override the default caption. This text will be formatted with markdown.',
                               blank=True, null=True, required=False)

    class Meta:
        icon = 'image'
        template = 'blog/captioned_image_block.html'
        label = 'Image'


class ExtraInformationBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    text = blocks.TextBlock(help_text='This text will be formatted with markdown.')

    class Meta:
        icon = 'plus'
        template = 'blog/extra_information_block.html'
        label = 'Extra Information'


class CodeBlock(blocks.TextBlock):
    class Meta:
        template = 'blog/code_blog.html'
        icon = 'code'
        label = 'Code'


class SubjectPanelField(Orderable):
    page = ParentalKey('ArticlePage', related_name='subjects')
    subject = models.ForeignKey(SubjectSnippet)

    panels = [
        SnippetChooserPanel('subject'),
    ]

    def __unicode__(self):
        return unicode(self.subject)


class ArticlePage(Page):
    parent_page_types = ["ArticleIndexPage"]
    subpage_types = []

    author = models.ForeignKey(
        'AuthorPage',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    main_image = models.ForeignKey(
        'images.CustomImage',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    date = models.DateField("Post date")
    intro = models.TextField(
        max_length=250,
        help_text='This will only appear in article previews, not with the full article. This text will be formatted with markdown.')
    body = StreamField([
        ('text', blocks.TextBlock(icon='pilcrow', help_text='This text will be formatted with markdown.')),
        ('image', CaptionedImageBlock()),
        ('embed', EmbedBlock(icon='media')),
        ('extra_information', ExtraInformationBlock()),
    ])

    search_fields = Page.search_fields + (
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('author')
    )

    content_panels = Page.content_panels + [
        PageChooserPanel('author'),
        InlinePanel('subjects', label='Subjects'),
        FieldPanel('date'),
        InlinePanel('source_links', label="Sources"),
        ImageChooserPanel('main_image'),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
    ]

    class Meta:
        verbose_name = "Article"

    def __unicode__(self):
        return self.title

    def article_index(self):
        # Find closest ancestor which is article page
        return self.get_ancestors().type(ArticleIndexPage).last()

    """def subject(self):
        # TODO: Replace/remove
        subject = ArticleIndexPage.objects.ancestor_of(self).last().subject
        if subject is not None:
            return subject
        else:
            return ""
    """

    def all_subjects(self):
        # TODO: Replace/remove
        subjects = []
        for s in SubjectSnippet.objects.all():
            subjects.append(ArticleIndexPage.objects.filter(subject=s)[0])
        return subjects


class SourceLink(models.Model):
    title = models.TextField(max_length=1023, help_text="This text will be formatted with markdown. Use a standard citation format.", blank=True, null=True)
    url = models.URLField('Link to Source', blank=True, null=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('url'),
    ]

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True


class ArticleSourceLink(Orderable, SourceLink):
    page = ParentalKey('ArticlePage', related_name='source_links')


class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
    ]

    class Meta:
        abstract = True


# Related links
class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class ArticleIndexRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('ArticleIndexPage', related_name='related_links')


class ArticleIndexPage(Page):
    subpage_types = ['ArticlePage']

    subject = models.OneToOneField(
        SubjectSnippet,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+")
    intro = models.TextField(
        blank=True,
        help_text='This text will be formatted with markdown.')

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        SnippetChooserPanel('subject', SubjectSnippet),
        #InlinePanel('related_links', label="Related links"),
    ]

    class Meta:
        verbose_name = 'Article Index'


    def get_context(self, request, *args, **kwargs):
        context = super(ArticleIndexPage, self).get_context(
            request, *args, **kwargs)
        articles = self.articles()

        # Pagination
        page = request.GET.get('page')
        page_size = 10
        from home.models import GeneralSettings
        if GeneralSettings.for_site(request.site).pagination_count:
            page_size = GeneralSettings.for_site(request.site).pagination_count

        if page_size is not None:
            paginator = Paginator(articles, page_size)
            try:
                articles = paginator.page(page)
            except PageNotAnInteger:
                articles = paginator.page(1)
            except EmptyPage:
                articles = paginator.page(paginator.num_pages)

        context['articles'] = articles
        return context


    def articles(self, subject_filter=None):
        """
        Return all articles if no subject specified, otherwise only those from that Subject
        :param subject_filter: Subject
        :return: QuerySet of Articles (I think)
        """
        articles = ArticlePage.objects.live().descendant_of(self)
        if subject_filter is not None:
            articles = articles.filter(subject=subject_filter)
        articles = articles.order_by('-date')
        return articles


class AuthorPage(Page):
    parent_page_types = ['AuthorIndexPage']
    subpage_types = []

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL, )
    portrait = models.ForeignKey(
        'images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    bio = models.TextField(
        max_length=800,
        null=True, blank=True,
        help_text='This text will be formatted with markdown.')
    personal_website = models.URLField(blank=True)

    content_panels = [
        FieldPanel('title'),
        FieldPanel('user'),
        FieldPanel('bio'),
        ImageChooserPanel('portrait'),
        FieldPanel('personal_website'),
    ]

    def author_articles(self):
        return ArticlePage.objects.live().filter(author=self).order_by('title')

    def __unicode__(self):
        return self.title


class AuthorIndexPage(Page):
    subpage_types = ['AuthorPage']

    intro = models.TextField(
        blank=True,
        help_text='This text will be formatted with markdown.')

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    def authors(self):
        return AuthorPage.objects.all()
