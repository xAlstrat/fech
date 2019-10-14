from django_cron import CronJobBase, Schedule

from blog.notifications import send_notifications


class SendNotificationsJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'blog.send_notifications'    # a unique code

    def do(self):
        send_notifications()
        print('Notifications sent!')