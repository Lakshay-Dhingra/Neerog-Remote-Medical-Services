import random
import time
from .task import Scheduler, Email_Notifications
from apscheduler.schedulers.background import BackgroundScheduler

from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
scheduler1 = BackgroundScheduler()
scheduler1.add_jobstore(DjangoJobStore(), "default")


@register_job(scheduler, "interval", hours=24, replace_existing=True)
def test_job():
    Scheduler()
    # raise ValueError("Olala!")
register_events(scheduler)
scheduler.start()
@register_job(scheduler1, "interval", hours=1, replace_existing=True)
def test_job():
    Email_Notifications()

register_events(scheduler1)

scheduler1.start()
print("Scheduler started!")