from django.core.management import BaseCommand

from blog.notifications import send_notifications


class Command(BaseCommand):
    help = 'Send notifications'

    def add_arguments(self, parser):
        parser.add_argument('--create',
                            action='store_true',
                            dest='create',
                            help='Creates dummy student users')
        parser.add_argument('--delete',
                            action='store_true',
                            dest='delete',
                            help='Deletes dummy student users')
        parser.add_argument('--reset',
                            action='store_true',
                            dest='reset',
                            help='Resets dummy student users')


    def notify(self):
        send_notifications()


    def handle(self, *args, **options):
        self.notify()