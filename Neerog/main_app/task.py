from .views import *
from .models import *;
def Scheduler():
    for i in Appointment_Timings.objects.all():
        dt=datetime.datetime.now()
        if(i.date<dt.date()):
            i.delete();