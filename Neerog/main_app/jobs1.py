from .task import Email_Notifications
from apscheduler.schedulers.background import BackgroundScheduler

from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

scheduler1 = BackgroundScheduler()
scheduler1.add_jobstore(DjangoJobStore(), "default")

@register_job(scheduler1, "interval", hours=1, replace_existing=True)
def test_job():
    Email_Notifications()

register_events(scheduler1)
scheduler1.start()
print("Scheduler1 started!")

