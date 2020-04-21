# api.py
import re

from django.db import models
from django.utils.timezone import now
from modelcluster.models import get_all_child_relations
from rest_framework.filters import BaseFilterBackend
from taggit.managers import TaggableManager
from wagtail.api.v2.endpoints import PagesAPIEndpoint, BaseAPIEndpoint
from wagtail.api.v2.filters import OrderingFilter, FieldsFilter
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.serializers import ChildRelationField, BaseSerializer
from wagtail.api.v2.utils import parse_boolean, BadRequestError
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint

from blog.models import Event, New, Benefit, Place, CCEE, ONG, Transparency, Archive, CEFECHContent


class CustomFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        This performs field level filtering on the result set
        Eg: ?title=James Joyce
        """
        fields = set(view.get_available_fields(queryset.model, db_fields_only=True))
        query_parameters = view.request.GET.keys()
        query_parameters = set(filter(lambda param: re.sub(r'__.*$', '', param) in fields and param.find('__') != -1, query_parameters))
        fields = fields.union(query_parameters)

        for field_name, value in request.GET.items():
            if field_name in fields:
                lookup = ''
                if '__' in field_name:
                    i = field_name.find('__')
                    lookup = field_name[i:]
                    field_name = field_name[:i]
                try:
                    field = queryset.model._meta.get_field(field_name)
                except LookupError:
                    field = None

                # Convert value into python
                try:
                    if isinstance(field, (models.BooleanField, models.NullBooleanField)):
                        value = parse_boolean(value)
                    elif isinstance(field, (models.IntegerField, models.AutoField)):
                        value = int(value)
                except ValueError as e:
                    raise BadRequestError("field filter error. '%s' is not a valid value for %s (%s)" % (
                        value,
                        field_name,
                        str(e)
                    ))

                if isinstance(field, TaggableManager):
                    for tag in value.split(','):
                        queryset = queryset.filter(**{field_name + '__name': tag})

                    # Stick a message on the queryset to indicate that tag filtering has been performed
                    # This will let the do_search method know that it must raise an error as searching
                    # and tag filtering at the same time is not supported
                    queryset._filtered_by_tag = True
                else:
                    field_name = field_name + lookup
                    queryset = queryset.filter(**{field_name: value})

        return queryset


class SnippetApiEndpoint(BaseAPIEndpoint):
    known_query_parameters = BaseAPIEndpoint.known_query_parameters.union([
        'type',
    ])
    filter_backends = [
        CustomFilterBackend,
        OrderingFilter
    ]



    # @classmethod
    # def get_available_fields(cls, model, db_fields_only=False):
    #     return super().get_available_fields(model, db_fields_only) + [
    #         'publish_at__lte',
    #         'publish_at__lt',
    #         'publish_at__gt',
    #         'publish_at__gte',
    #     ]

    def check_query_parameters(self, queryset):
        """
        Ensure that only valid query paramters are included in the URL.
        """
        query_parameters = self.request.GET.keys()
        query_parameters = set(map(lambda param: re.sub(r'__.*$', '', param ), query_parameters))

        # All query paramters must be either a database field or an operation
        allowed_query_parameters = set(self.get_available_fields(queryset.model, db_fields_only=True)).union(self.known_query_parameters)
        unknown_parameters = query_parameters - allowed_query_parameters
        if unknown_parameters:
            raise BadRequestError("query parameter is not an operation or a recognised field: %s" % ', '.join(sorted(unknown_parameters)))


class EventSnippetAPIEndpoint(SnippetApiEndpoint):
    model = Event

    def get_queryset(self):
        return self.model.objects.exclude(unpublish_at__isnull=False, unpublish_at__lte=now()).all().order_by('id')


class NewSnippetAPIEndpoint(SnippetApiEndpoint):
    model = New

    def get_queryset(self):
        return self.model.objects.exclude(unpublish_at__isnull=False, unpublish_at__lte=now()).all().order_by('id')

class BenefitSnippetAPIEndpoint(SnippetApiEndpoint):
    model = Benefit
    # body_fields = BaseAPIEndpoint.body_fields + [
    #     'field_1',
    #     'field_2',
    #     'field_3',
    # ]
#
    # listing_default_fields = BaseAPIEndpoint.listing_default_fields = [
    #     'field_1',
    #     'field_2',
    #     'field_3',
    # ]

    def get_queryset(self):
        return self.model.objects.exclude(unpublish_at__isnull=False, unpublish_at__lte=now()).all().order_by('id')


class PlaceSnippetAPIEndpoint(SnippetApiEndpoint):
    model = Place
    listing_default_fields = BaseAPIEndpoint.listing_default_fields + [
        'name',
        'address',
        'lat',
        'lng',
    ]


class CCEESnippetAPIEndpoint(SnippetApiEndpoint):
    model = CCEE

    def get_queryset(self):
        return self.model.objects.filter(published=True).all().order_by('title')


class ONGSnippetAPIEndpoint(SnippetApiEndpoint):
    model = ONG

    def get_queryset(self):
        return self.model.objects.filter(published=True).all().order_by('title')


class TransparencySnippetAPIEndpoint(SnippetApiEndpoint):
    model = Transparency

    def get_queryset(self):
        return self.model.objects.filter(published=True).all().order_by('title')


class ArchiveSnippetAPIEndpoint(SnippetApiEndpoint):
    model = Archive

    def get_queryset(self):
        return self.model.objects.filter(published=True).all().order_by('-published_at')


class CEFECHSnippetAPIEndpoint(SnippetApiEndpoint):
    model = CEFECHContent

    def get_queryset(self):
        return self.model.objects.filter(published=True).all().order_by('-published_at')

# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
# api_router.register_endpoint('pages', PagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)
api_router.register_endpoint('events', EventSnippetAPIEndpoint)
api_router.register_endpoint('benefits', BenefitSnippetAPIEndpoint)
api_router.register_endpoint('news', NewSnippetAPIEndpoint)
api_router.register_endpoint('places', PlaceSnippetAPIEndpoint)
api_router.register_endpoint('ccees', CCEESnippetAPIEndpoint)
api_router.register_endpoint('ongs', ONGSnippetAPIEndpoint)
api_router.register_endpoint('transparency', TransparencySnippetAPIEndpoint)
api_router.register_endpoint('archives', ArchiveSnippetAPIEndpoint)
api_router.register_endpoint('cefech', CEFECHSnippetAPIEndpoint)