# api.py
from modelcluster.models import get_all_child_relations
from wagtail.api.v2.endpoints import PagesAPIEndpoint, BaseAPIEndpoint
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.serializers import ChildRelationField, BaseSerializer
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint

from blog.models import Event, New, Benefit


class SnippetApiEndpoint(BaseAPIEndpoint):
    known_query_parameters = BaseAPIEndpoint.known_query_parameters.union([
        'type',
    ])


class EventSnippetAPIEndpoint(SnippetApiEndpoint):
    model = Event


class NewSnippetAPIEndpoint(SnippetApiEndpoint):
    model = New


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

# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', PagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)
api_router.register_endpoint('events', EventSnippetAPIEndpoint)
api_router.register_endpoint('benefits', BenefitSnippetAPIEndpoint)
api_router.register_endpoint('news', NewSnippetAPIEndpoint)