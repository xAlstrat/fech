from django.db.models import F

from blog.models import EventNotification
from notifications.notifiers import BaseNotificationProvider, EmailNotificationSender
from django.contrib.auth.models import User


def send_notifications():
    send_email_notifications()


def send_email_notifications():
    provider = BaseNotificationProvider(EventNotification.objects)
    sender = EmailNotificationSender(provider, 'event')
    sender.send_notifications(User.objects.all())