from blog.models import EventNotification, NewNotification, BenefitNotification
from notifications.notifiers import BaseNotificationProvider, EmailNotificationSender, PushNotificationSender
from django.contrib.auth.models import User


def send_notifications():
    send_email_notifications()
    send_push_notifications()


def send_email_notifications():
    users = User.objects.all()
    provider = BaseNotificationProvider(EventNotification.objects)
    sender = EmailNotificationSender(provider, 'event', title='BenefiCh - ¡Se ha añadido un evento!')
    sender.send_notifications(users)

    provider = BaseNotificationProvider(NewNotification.objects)
    sender = EmailNotificationSender(provider, 'new', title='BenefiCh - ¡Se ha añadido una noticia!')
    sender.send_notifications(users)

    provider = BaseNotificationProvider(BenefitNotification.objects)
    sender = EmailNotificationSender(provider, 'benefit', title='BenefiCh - ¡Hay un nuevo beneficio para ti!')
    sender.send_notifications(users)


def send_push_notifications():
    users = User.objects.all()
    provider = BaseNotificationProvider(EventNotification.objects)
    sender = PushNotificationSender(provider, 'event', title='¡Se ha añadido un evento!', topic='events')
    sender.send_notifications(users)

    provider = BaseNotificationProvider(NewNotification.objects)
    sender = PushNotificationSender(provider, 'new', title='¡Se ha añadido una noticia!', topic='news')
    sender.send_notifications(users)

    provider = BaseNotificationProvider(BenefitNotification.objects)
    sender = PushNotificationSender(provider, 'benefit', title='¡Hay un nuevo beneficio para ti!', topic='eventsAt{{place_id}}')
    sender.send_notifications(users)