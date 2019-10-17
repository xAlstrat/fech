from django.db.models import F

from blog.models import  EventSharing
from social.publishers import BasePublicationProvider, TwitterPublisher, InstagramPublisher


def create_publications():
    create_twitter_publications()
    create_instagram_publications()


def create_twitter_publications():
    provider = BasePublicationProvider(EventSharing.objects)

    sender = TwitterPublisher(provider, 'event')
    sender.post_publications()


def create_instagram_publications():
    provider = BasePublicationProvider(EventSharing.objects)

    sender = InstagramPublisher(provider, 'event')
    sender.post_publications()