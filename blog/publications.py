from django.db.models import F

from blog.models import EventSharing, NewSharing, BenefitSharing
from social.publishers import BasePublicationProvider, TwitterPublisher, InstagramPublisher

"""
Create publications for specified social networks.
"""
def create_publications():
    create_twitter_publications()
    create_instagram_publications()


def create_twitter_publications():
    provider = BasePublicationProvider(EventSharing.objects)
    sender = TwitterPublisher(provider, 'event')
    sender.post_publications()

    provider = BasePublicationProvider(NewSharing.objects)
    sender = TwitterPublisher(provider, 'new')
    sender.post_publications()

    provider = BasePublicationProvider(BenefitSharing.objects)
    sender = TwitterPublisher(provider, 'benefit')
    sender.post_publications()


def create_instagram_publications():
    provider = BasePublicationProvider(EventSharing.objects)

    sender = InstagramPublisher(provider, 'event')
    sender.post_publications()

    provider = BasePublicationProvider(NewSharing.objects)
    sender = InstagramPublisher(provider, 'new')
    sender.post_publications()

    provider = BasePublicationProvider(BenefitSharing.objects)
    sender = InstagramPublisher(provider, 'benefit')
    sender.post_publications()