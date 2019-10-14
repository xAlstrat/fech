from datetime import datetime, time

import pytz
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import DecimalField
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from wagtail.api import APIField
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, TabbedInterface, ObjectList, \
    FieldRowPanel
from wagtail.core.rich_text import RichText
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from babel.dates import format_datetime, format_date
from django.utils.timezone import now

from blog.serializers import UserSerializer, RichTextRendereableField, get_place_serializer


class UnnorderedInlinePanel(InlinePanel):
    template = "panel/unnordered_inline_panel.html"


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)


    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label="Galería de imágenes"),
        InlinePanel('authors', label="Autores"),
    ]

    api_fields = [
        APIField('date'),
        APIField('intro'),
        APIField('body'),
        APIField('tags'),
        APIField('authors'),
    ]


class BlogPageAuthor(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='authors')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    panels = [
        SnippetChooserPanel('user'),
    ]

    api_fields = [
        APIField('user', serializer=UserSerializer()),
    ]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


class BlogTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context


# Snippets
@register_snippet
class Place(models.Model):
    name = models.CharField('Nombre', max_length=256)
    address = models.CharField('Dirección', max_length=256)
    lat = models.DecimalField(max_digits=9, decimal_places=7)
    lng = models.DecimalField(max_digits=9, decimal_places=7)

    api_fields = [
        APIField('name'),
        APIField('address'),
        APIField('lat'),
        APIField('lng'),
    ]

    def __str__(self):
        return '%s - %s' % (self.name, self.address)


class CreateMixin(models.Model):
    """
    Provides a mixin for annotating a DB object with timestamp and
    user information of creation.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    """
    Defines the date and time when the object is created at.
    """

    modified_at = models.DateTimeField(auto_now_add=True)
    """
    Relates to the user whom the object is created by.
    """

    class Meta:
        abstract = True


class ContentTags(TaggedItemBase):
    content_object = ParentalKey(
        'Content',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class Content(CreateMixin, ClusterableModel):
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.DO_NOTHING, related_name='+', verbose_name="Imagen"
    )
    title = models.CharField(max_length=250, verbose_name='Título')
    body = RichTextField(blank=True, verbose_name="Descripción")
    tags = TaggableManager(through=ContentTags, blank=True)
    publish_at = models.DateTimeField('Publicar el', default=now)
    unpublish_at = models.DateTimeField('Despublicar el', null=True, blank=True)

    search_fields = [
        index.SearchField('body'),
    ]

    panels = [
        FieldPanel('title', classname='title'),
        FieldPanel('body', classname="full"),
        ImageChooserPanel('image', heading='heading'),
    ]

    end_panels = [
        FieldPanel('author'),
        FieldPanel('tags'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('publish_at', classname="col6", heading='heading'),
                FieldPanel('unpublish_at', classname="col6"),
            ])
        ], heading="Publicar automáticamente", help_text='Agenda este contenido para ser publicado y/o despublicado automáticamente. Si el campo \'despublicar\' está vacío no se agendará la despublicación.'),
        UnnorderedInlinePanel('notifications', label="Notificación automática", help_text='Selecciona un canal, una fecha y hora para notificar este contenido automáticamente a todos los estudiantes suscritos.'),
        UnnorderedInlinePanel('sharings', label="Publicación en red social", help_text='Selecciona una red social, una fecha y hora para publicar este contenido automáticamente en dicha red social.')
    ]

    api_fields = [
        APIField('title'),
        APIField('body', serializer=RichTextRendereableField()),
        APIField('image'),
        APIField('author', serializer=UserSerializer()),
        APIField('tags'),
    ]

    @property
    def body_as_html(self):
        rich_text = RichText(self.body)
        return rich_text.__html__()

    def __str__(self):
        tz = pytz.timezone("America/Santiago")
        date = format_datetime(self.created_at.astimezone(tz), 'dd/MMM/YYYY', locale='es')
        return '%s. %s' % (date, self.title)


@register_snippet
class Event(Content):
    start = models.DateTimeField("Fecha de inicio")
    end = models.DateTimeField("Fecha de término", null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING, null=True)

    search_fields = Content.search_fields + [

    ]

    panels = Content.panels + [
        MultiFieldPanel([
            FieldRowPanel([
              FieldPanel('start', classname="col6"),
              FieldPanel('end', classname="col6"),
            ])
        ], heading="Fecha del evento"),
        FieldPanel('place')
    ] + Content.end_panels

    api_fields = Content.api_fields + [
        APIField('start'),
        APIField('end'),
        APIField('place', serializer=get_place_serializer()),
    ]

    # edit_handler = TabbedInterface([
    #     ObjectList(panels, heading="Contenido"),
    #     ObjectList([
    #         UnnorderedInlinePanel('notifications', label="Notificaciones"),
    #     ], heading="Notificar"),
    #     ObjectList([
    #         UnnorderedInlinePanel('sharings', label="Pendientes"),
    #     ], heading="Compartir"),
    # ])

    def __str__(self):
        tz = pytz.timezone("America/Santiago")
        date = format_datetime(self.start.astimezone(tz), 'dd/MMM/YYYY', locale='es')
        time = format_datetime(self.start.astimezone(tz), 'HH:mm', locale='es')
        if self.end:
            time = time + (' - %s' % format_datetime(self.end.astimezone(tz), 'HH:mm', locale='es'))
        return '%s, %s. %s' % (date, time, self.title)


@register_snippet
class New(Content):

    search_fields = Content.search_fields + [
    ]

    panels = Content.panels + [
    ] + Content.end_panels

    api_fields = Content.api_fields + [
    ]


@register_snippet
class Benefit(Content):
    start = models.DateField("Fecha de inicio", null=True, blank=True)
    end = models.DateField("Fecha de término", null=True, blank=True)

    search_fields = Content.search_fields + [
    ]

    panels = Content.panels + [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('start', classname="col6"),
                FieldPanel('end', classname="col6"),
            ])
        ], heading="Fecha del beneficio"),
    ] + Content.end_panels

    api_fields = Content.api_fields + [
        APIField('start'),
        APIField('end')
    ]

    def __str__(self):
        date = format_date(self.start, 'dd/MMM/YYYY', locale='es')
        return '%s. %s' % (date, self.title)


class Notification(CreateMixin):

    CHANNEL_EMAIL = 'EMAIL'
    CHANNEL_MOBILE = 'MOBILE'
    notify_at = models.DateTimeField("Fecha de notificación", default=now)
    notified = models.BooleanField("Se ha notificado", default=False)
    channel = models.CharField('Canal', max_length=16, choices=[
        (CHANNEL_EMAIL, 'E-mail'),
        (CHANNEL_MOBILE, 'App'),
    ], default=CHANNEL_EMAIL)
    limit = models.Q(app_label='blog', model='event') | models.Q(app_label='blog', model='new')|\
            models.Q(app_label='blog', model='benefit')
    # contentNotificación_type = models.ForeignKey(
    #     ContentType,
    #     verbose_name='Contenido',
    #     limit_choices_to=limit,
    #     on_delete=models.CASCADE
    # )
    # object_id = models.PositiveIntegerField(
    #     verbose_name='Objeto relacionado',
    #     null=True,
    # )
    # content_object = GenericForeignKey('content_type', 'object_id')

    search_fields = Content.search_fields + [
    ]

    panels = [
        FieldRowPanel([
            FieldPanel('notify_at', classname="col6"),
            FieldPanel('channel', classname="col6"),
        ], heading="Fecha de notificación",
            classname="collapsible collapsed"),
    ]

    api_fields = Content.api_fields + [
        APIField('notify_at'),
        APIField('notified'),
        APIField('channel'),
    ]


class Sharing(CreateMixin):

    SOCIAL_FACEBOOK = 'FACEBOOK'
    SOCIAL_INSTAGRAM = 'INSTAGRAM'
    SOCIAL_TWITTER = 'TWITTER'
    notify_at = models.DateTimeField("Fecha de notificación", default=now)
    notified = models.BooleanField("Se ha notificado", default=False)
    channel = models.CharField('Red social', max_length=32, choices=[
        (SOCIAL_FACEBOOK, 'Facebook'),
        (SOCIAL_INSTAGRAM, 'Instagram'),
        (SOCIAL_TWITTER, 'Twitter'),
    ], default=SOCIAL_FACEBOOK)

    search_fields = Content.search_fields + [
    ]

    panels = [
        FieldRowPanel([
            FieldPanel('notify_at', classname="col6"),
            FieldPanel('channel', classname="col6"),
        ], heading="Compartir el",
            classname="collapsible collapsed")
    ]

    api_fields = Content.api_fields + [
        APIField('notify_at'),
        APIField('notified'),
        APIField('channel'),
    ]


class EventNotification(Notification, Orderable):
    event = ParentalKey(to='blog.Event', on_delete=models.CASCADE, related_name='notifications')

    class Meta:
        ordering = ['-created_at']


class BenefitNotification(Notification, Orderable):
    benefit = ParentalKey(to='blog.Benefit', on_delete=models.CASCADE, related_name='notifications')

    class Meta:
        ordering = ['-created_at']


class NewNotification(Notification, Orderable):
    new = ParentalKey(to='blog.New', on_delete=models.CASCADE, related_name='notifications')

    class Meta:
        ordering = ['-created_at']


class EventSharing(Sharing, Orderable):
    event = ParentalKey(to='blog.Event', on_delete=models.CASCADE, related_name='sharings')

    class Meta:
        ordering = ['-created_at']


class BenefitSharing(Sharing, Orderable):
    benefit = ParentalKey(to='blog.Benefit', on_delete=models.CASCADE, related_name='sharings')

    class Meta:
        ordering = ['-created_at']


class NewSharing(Sharing, Orderable):
    new = ParentalKey(to='blog.New', on_delete=models.CASCADE, related_name='sharings')

    class Meta:
        ordering = ['-created_at']

register_snippet(User)