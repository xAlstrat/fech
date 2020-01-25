
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.timezone import now

from django.core import mail
from pyfcm import FCMNotification
from wagtail.api.v2.serializers import BaseSerializer

from fech.settings.base import FIREBASE_API_KEY
from django.template import Template, Context

"""
Given a query set, it obtains a filtered notification list
"""
class BaseNotificationProvider:
    """
    Specifies when the notification should be send (Datetime)
    """
    notify_at_field = 'notify_at'

    """
    Specifies if the notification is already sent
    """
    notified_field = 'notified'

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


class BaseNotificationSender:
    channel = None

    def __init__(self, provider, title='Tienes una notificación'):
        self.provider = provider
        self.notifications = self.provider.get_notifications(self.channel)
        self.title = title

    def send_notifications(self, users):
        print('Sending %d notifications through %s' % (self.notifications.count(), self.channel))
        sent = self.send(self.notifications, users)
        if sent:
            self.after_send()

    def send(self, notifications, users):
        pass

    def after_send(self):
        self.notifications.update(**{self.provider.notified_field: True})


class EmailNotificationSender(BaseNotificationSender):

    channel = 'EMAIL'
    template_field = 'template'
    object_notification_mapping = {
        'subject': 'title',
        'body': 'body_as_html',
        'from_email': '',
        'to': '',
        'cc': '',
        'reply_to': ''
    }

    def __init__(self, provider, object_field, title='Tienes una notificación'):
        super().__init__(provider, title='Tienes una notificación')
        self.object_field = object_field

    def get_object(self, notification):
        return getattr(notification, self.object_field)

    def build_notification_message(self, notification, users):
        object_data = self.get_object(notification)
        template = get_template('notifications/default_email.html')
        msg = EmailMultiAlternatives(
            subject=self.title,
            body='',
            from_email='Notificaciones <' + 'report@suplebest.cl' + '>',
            to=list(map(lambda u: u.email, users)),
            cc=[],
            reply_to=['dudas@fech.cl']
        )

        html_message = template.render(object_data.__dict__)
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return msg

    def build_messages(self, notifications, users):
        messages = []
        for notification in notifications:
            messages.append(self.build_notification_message(notification, users))
        return messages

    def send(self, notifications, users):
        messages = self.build_messages(notifications, users)
        connection = mail.get_connection()
        if len(messages) > 0:
            connection.send_messages(messages)
            return True
        return False


class PushNotificationSender(BaseNotificationSender):

    channel = 'MOBILE'
    template_field = 'template'
    object_notification_mapping = {
        'subject': 'title',
        'body': 'body_as_html',
    }

    def get_object(self, notification):
        return getattr(notification, self.object_field)

    def __init__(self, provider, object_field, title, serializer):
        super().__init__(provider, title=title)
        self.object_field = object_field
        self.serializer = serializer

    def build_notification_body(self, notification):
        object_data = self.get_object(notification)
        template_str = getattr(object_data, self.object_notification_mapping.get('subject'))
        template = Template(template_str)
        return template.render(Context(object_data.__dict__))

    def send(self, notifications, users):
        for notification in notifications:
            object_data = self.get_object(notification)
            push_service = FCMNotification(api_key=FIREBASE_API_KEY)
            response = push_service.notify_topic_subscribers(
                topic_name="global",
                message_body=self.build_notification_body(notification),
                message_title=self.title,
                click_action='FLUTTER_NOTIFICATION_CLICK',
                data_message={
                    'type': self.object_field,
                    'id': object_data.pk
                }
            )
        return True
