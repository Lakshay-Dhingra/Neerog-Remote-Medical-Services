import random
import time
from .task import Scheduler
from apscheduler.schedulers.background import BackgroundScheduler

from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


@register_job(scheduler, "interval", hours=24, replace_existing=True)
def test_job():
    Scheduler()
    # raise ValueError("Olala!")


register_events(scheduler)

scheduler.start()
print("Scheduler started!")