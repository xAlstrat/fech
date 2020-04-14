from datetime import datetime, time

import pytz
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import DecimalField
from django.utils.html import format_html
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from fcm_django.models import FCMDevice
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from wagtail.api import APIField
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, TabbedInterface, ObjectList, \
    FieldRowPanel, EditHandler
from wagtail.core.rich_text import RichText
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from babel.dates import format_datetime, format_date
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from blog.serializers import UserSerializer, RichTextRendereableField, get_place_serializer


class ReadOnlyPanel(EditHandler):
    """
    Base Handler for rendering read only fields.
    """
    def __init__(self, attr, *args, **kwargs):
        self.attr = attr
        super().__init__(*args, **kwargs)

    def clone(self):
        return self.__class__(
            attr=self.attr,
            heading=self.heading,
            classname=self.classname,
            help_text=self.help_text,
        )

    def get_heading(self):
        return self.heading

    def render(self):
        value = getattr(self.instance, self.attr)
        if callable(value):
            value = value()
        return format_html('<div style="padding-top: 1.2em;">{}</div>', value)

    def render_as_object(self):
        return format_html(
            '<fieldset><legend>{}</legend>'
            '<ul class="fields"><li><div class="field">{}</div></li></ul>'
            '</fieldset>',
            self.get_heading(), self.render())

    def render_as_field(self):
        return format_html(
            '<div class="field">'
            '<label>{}{}</label>'
            '<div class="field-content">{}</div>'
            '</div>',
            self.get_heading(), _(':'), self.render())


class WithRequestObjectList(ObjectList):

    def get_form_class(self):
        request = self.request
        class Form(super().get_form_class()):
            def save(self, *args, **kwargs):
                object = super().save(*args, **kwargs)
                after_save = getattr(object, "after_save", None)
                if callable(after_save):
                    return object.after_save(request)
                return object
        return Form


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

    class Meta:
        verbose_name = "Lugar"
        verbose_name_plural = "Lugares"

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
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.DO_NOTHING, related_name='+', verbose_name="Imagen"
    )
    title = models.CharField(max_length=250, verbose_name='Título')
    body = RichTextField(blank=True, verbose_name="Descripción")
    tags = TaggableManager(through=ContentTags, blank=True)
    publish_at = models.DateTimeField('Publicar el', default=now)
    unpublish_at = models.DateTimeField('Despublicar el', null=True, blank=True)
    pinned = models.BooleanField('Destacar', default=False, help_text='Destacar el contenido para que aparezca al comienzo.')


    search_fields = [
        index.SearchField('body'),
    ]

    panels = [
        FieldPanel('title', classname='title'),
        FieldPanel('body', classname="full"),
        ImageChooserPanel('image', heading='heading'),
        FieldPanel('pinned', classname="full"),
    ]

    end_panels = [
        ReadOnlyPanel('author', heading="Autor"),
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
        APIField('publish_at'),
        APIField('pinned'),
    ]

    @property
    def image_path(self):
        return self.image.file.path

    @property
    def body_as_html(self):
        rich_text = RichText(self.body)
        return rich_text.__html__()

    def __str__(self):
        date = format_datetime(self.created_at.astimezone(pytz.timezone("America/Santiago")), 'dd/MMM/YYYY', locale='es')
        return '%s. %s - %s' % (date, self.title, self.get_published_label())

    def after_save(self, request):
        self.author = request.user
        return self.save()

    def is_published(self):
        dt_now = now()
        if (self.publish_at is not None and self.publish_at < dt_now) and (self.unpublish_at is None or self.unpublish_at > dt_now):
            return True
        return False

    def was_unpublished(self):
        dt_now = now()
        if self.unpublish_at is not None and self.unpublish_at < dt_now:
            return True
        return False

    def is_pinned(self):
        return self.pinned

    def get_published_label(self):
        if self.was_unpublished():
            label = 'Publicación finalizada'
        elif self.is_published():
            label = 'Publicado'
        else:
            dt_now = now()
            days = (self.publish_at - dt_now).days
            label = 'queda %d día' if days == 1 else 'quedan %d días'
            label = ('Por publicar (%s)' % label) % days
        label = '%s%s' % ('📌 ' if self.is_pinned() else '', label)
        return label + self.get_notification_labels() + self.get_sharing_labels()

    def get_notification_labels(self):
        label = ''
        mobile_notifications = self.notifications.filter(channel='MOBILE')
        email_notifications = self.notifications.filter(channel='EMAIL')
        if mobile_notifications.count():
            count = mobile_notifications.filter(notified=True).count()
            label = label + ' 🔔%d' % count
        if email_notifications.count():
            count = email_notifications.filter(notified=True).count()
            label = label + ' @%d' % count
        return label

    def get_sharing_labels(self):
        label = ''
        twitter_notifications = self.sharings.filter(channel='TWITTER')
        ig_notifications = self.sharings.filter(channel='INSTAGRAM')
        if twitter_notifications.count():
            count = twitter_notifications.filter(published=True).count()
            label = label + ' 🕊%d' % count
        if ig_notifications.count():
            count = ig_notifications.filter(published=True).count()
            label = label + ' ⧇%d' % count
        return label


@register_snippet
class Event(Content):
    start = models.DateTimeField("Fecha de inicio")
    end = models.DateTimeField("Fecha de término", null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ('-publish_at',)

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

    edit_handler = WithRequestObjectList(panels)

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
        return '%s, %s. %s - %s' % (date, time, self.title, self.get_published_label())


@register_snippet
class New(Content):

    class Meta:
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"
        ordering = ('-publish_at',)

    search_fields = Content.search_fields + [
    ]

    panels = Content.panels + [
    ] + Content.end_panels

    edit_handler = WithRequestObjectList(panels)

    api_fields = Content.api_fields + [
    ]


@register_snippet
class Benefit(Content):
    start = models.DateField("Fecha de inicio", null=True, blank=True)
    end = models.DateField("Fecha de término", null=True, blank=True)

    class Meta:
        verbose_name = "Beneficio"
        verbose_name_plural = "Beneficios"
        ordering = ('-publish_at',)

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

    edit_handler = WithRequestObjectList(panels)


    api_fields = Content.api_fields + [
        APIField('start'),
        APIField('end')
    ]

    def __str__(self):
        date = format_date(self.start, 'dd/MMM/YYYY', locale='es')
        return '%s. %s - %s' % (date, self.title, self.get_published_label())


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
    publish_at = models.DateTimeField("Fecha de publicación", default=now)
    published = models.BooleanField("Se ha publicado", default=False)
    description = models.TextField("Descripción", max_length=2048, help_text='Número máximo de carácteres depende de la red social utilizada.', null=True)
    channel = models.CharField('Red social', max_length=32, choices=[
        # (SOCIAL_FACEBOOK, 'Facebook'),
        (SOCIAL_INSTAGRAM, 'Instagram'),
        (SOCIAL_TWITTER, 'Twitter'),
    ], default=SOCIAL_INSTAGRAM)

    search_fields = Content.search_fields + [
    ]

    panels = [
        FieldRowPanel([
            FieldPanel('publish_at', classname="col6"),
            FieldPanel('channel', classname="col6"),
            FieldPanel('description', classname="col12"),
            ReadOnlyPanel('published', classname="col12", heading='¿Publicado?'),
        ], heading="Publicar el",
            classname="collapsible collapsed")
    ]

    api_fields = Content.api_fields + [
        APIField('publish_at'),
        APIField('published'),
        APIField('description'),
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