from .views import *
from .models import *;
from . import domain
from Neerog import secret_settings,settings
def Scheduler():
    for i in Appointment_Timings.objects.all():
        dt=datetime.datetime.now()
        if(i.date<dt.date()):
            i.delete();

def Email_Notifications():
    dt=datetime.datetime.now()
    for i in Appointments.objects.filter(appointment_date=dt):
        p = i.appointment_time
        p1 = i.appointment_date
        dt = datetime.datetime.now()
        dt1 = datetime.datetime(int(p1.strftime("%Y")), int(p1.strftime("%m")), int(p1.strftime("%d")),
                                int(p.strftime("%H")), int(p.strftime("%M")), int(p.strftime("%S")))
        k = dt1 - dt
        #print(k.total_seconds())
        if(k.total_seconds()<=3600 and k.total_seconds() > 0):
            if(i.doctoremail):
                user = UserDetails.objects.get(email=i.doctoremail)
                template = render_to_string('main_app/Email_Notification.html',
                                            {
                                                'meeting_url':i.meeting_url,
                                                'doctor_name':user.name,
                                                'appointment_id':i.appointmentid,
                                                'time':i.appointment_time,
                                                'domain': domain.getDomainName(),
                                            })
            else:
                template = render_to_string('main_app/Email_Notification.html',
                                            {
                                                'appointment_id': i.appointmentid,
                                                'time': i.appointment_time,
                                                'domain': '127.0.0.1:8000',
                                                'lab_name':i.TestingLabId.tlabid.name
                                            })

            email = EmailMessage(
                'Reminder related to Appointment',
                template,
                settings.EMAIL_HOST_USER,
                [i.patientemail],
            )
            email.fail_silently = False
            email.send()

