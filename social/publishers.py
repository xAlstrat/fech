
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.timezone import now

from django.core import mail
from sentry_sdk import capture_exception

from social.publish import publish_img_to_twitter, publish_img_to_instagram

"""
Given a query set, it obtains a filtered publication list
"""
class BasePublicationProvider:
    """
    Specifies when the notification should be send (Datetime)
    """
    notify_at_field = 'publish_at'

    """
    Specifies if the notification is already sent
    """
    notified_field = 'published'

    """
    Specifies which channel the notification belongs to
    """
    channel_field = 'channel'

    def __init__(self, notifications):
        self.notifications = notifications

    '''
    Get notifications that need to be send through the specified channel
    '''
    def get_notifications(self, channel):
        filters = {
            '{0}__{1}'.format(self.notify_at_field, 'lte'): now(),
            '{0}'.format(self.notified_field): False,
            '{0}'.format(self.channel_field): channel
        }
        return self.notifications.filter(**filters)


class BasePublisher:
    channel = None
    object_field = None

    object_notification_mapping = {
        'description': 'title',
        'media': 'image_path',
    }

    def __init__(self, provider, object_field):
        self.provider = provider
        self.notifications = self.provider.get_notifications(self.channel)
        self.object_field = object_field

    def post_publications(self):
        for publication in self.notifications:
            posted = False
            try:
                posted = self.post(publication)
            except Exception as e:
                print(e)
                capture_exception(e)
            if posted:
                setattr(publication, self.provider.notified_field, True)
                publication.save()
        self.after_post()

    def post(self, notification):
        pass

    def after_post(self):
        pass

    def get_object(self, notification):
        return getattr(notification, self.object_field)

    def get_publication_attr(self, publication, attr):
        return getattr(publication, self.object_notification_mapping.get(attr), None)


class TwitterPublisher(BasePublisher):

    channel = 'TWITTER'

    def post(self, publication):
        object_data = self.get_object(publication)
        description = self.get_publication_attr(object_data, 'description')
        media = self.get_publication_attr(object_data, 'media')
        publish_img_to_twitter(description=description, media=media)
        return True


class InstagramPublisher(BasePublisher):

    channel = 'INSTAGRAM'

    def post(self, publication):
        object_data = self.get_object(publication)
        description = self.get_publication_attr(object_data, 'description')
        media = self.get_publication_attr(object_data, 'media')
        publish_img_to_instagram(description=description, media=media)
        return True
