
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.timezone import now

from django.core import mail


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

    def __init__(self, provider):
        self.provider = provider
        self.notifications = self.provider.get_notifications(self.channel)

    def send_notifications(self, users):
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

    def __init__(self, provider, object_field):
        super().__init__(provider)
        self.object_field = object_field

    def get_object(self, notification):
        return getattr(notification, self.object_field)

    def build_notification_message(self, notification, users):
        object_data = self.get_object(notification)
        template = get_template('notifications/default_email.html')
        msg = EmailMultiAlternatives(
            subject=getattr(object_data, self.object_notification_mapping.get('subject')),
            body='',
            from_email='Notificaciones <' + 'notificationes@fech.cl' + '>',
            to=list(map(lambda u: u.email, users)),
            cc=[],
            reply_to=[]
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
