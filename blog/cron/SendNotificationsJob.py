from django_cron import CronJobBase, Schedule


class SendNotificationsJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'blog.send_notifications'    # a unique code

    def do(self):
        print("Cron job test")