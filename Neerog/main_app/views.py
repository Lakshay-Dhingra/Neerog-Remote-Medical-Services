import time
import random
from django.core.mail import send_mail, EmailMessage
from django.db.models import Sum,Avg,Q
from django.template.loader import render_to_string
from main_app.models import*;
from main_app.medical_tests import *;
from django.contrib import messages
from . import medical_speciality;
from django.contrib.auth.models import User,auth
import requests
import datetime
import json
import re
import json
import pandas as pd
from django.http import HttpResponse, JsonResponse
from geosky import geo_plug # library for geolocation
import datetime
import jwt
from django.shortcuts import render, redirect
from Neerog import secret_settings,settings
import random
# render syntax:
# return render(request,'page.html',context_var_dictionary)
from .medical_speciality import get_specialities
from .medical_tests import list_of_medical_tests

#time_slots="09:30,10:00,10:30,11:00,11:30,12:00,12:30,13:00,13:30,14:00,14:30,15:00,15:30,16:00,16:30,17:00"
# Create your views here.
replace_dictionary={"u0101":"a","u012b":"i","u016b":"u","u0100":"A","u016a":"u"}

# Verification of the user certificate
def verify(request):
    #email = request.session['email']
    user=UserDetails.objects.get(email=request.session['email'])
    p=dict()
    if(user.user_type=='Moderator'):
        p['Hospital']=Hospital.objects.filter(verified="No")
        p['Doctor']=Doctor.objects.filter(verified="No")
        p['Testing_Lab']=TestingLab.objects.filter(verified="No")
        return render(request,"main_app/Verify_Certificate.html",context={'list_of_certificates':p})
    else:
        messages.info(request, "You Can't Access This Page!")
        return redirect("/")

def verify_certificate(request,id):
    user=UserDetails.objects.get(userid=id)
    if(user.user_type=='Hospital'):
        p=Hospital.objects.get(hospitalid=user)
        p.verified="Yes"
        p.save()
    elif(user.user_type=='Doctor'):
        p=Doctor.objects.get(doctorid=user)
        p.verified="Yes"
        p.save()
    else:
        p=TestingLab.objects.get(tlabid=user)
        p.verified="Yes"
        p.save()
    user = UserDetails.objects.get(email=request.session['email'])
    p = dict()
    if (user.user_type == 'Moderator'):
        p['Hospital'] = Hospital.objects.filter(verified="No")
        # p['Clinic']=Hospital.objects.filter(verified="No").filter(clinic_name=)
        p['Doctor'] = Doctor.objects.filter(verified="No")
        p['Testing_Lab'] = TestingLab.objects.filter(verified="No")
        return render(request, "main_app/Verify_Certificate.html", context={'list_of_certificates': p})
    else:
        messages.info(request, "You Can't Access This Page!")
        return redirect("/")

def appoin(list_of_Appointments):
    dict={}
    for i in list_of_Appointments:
        if (i.Prescription!=""):
            dict[i] = i
        else:
            dict[i] = "Upload Prescription"
    return dict
def profile(request):
    dt = datetime.datetime.today()
    email=request.session['email']
    no_of_Appointments_completed=0;
    no_of_Appointments=0;
    available=True;
    user=UserDetails.objects.get(email=email)
    if(user.user_type=='Hospital'):
        dt = datetime.datetime.today()
        Appointments1 = []
        appointments_this_month = 0;
        earning_this_month = 0;
        appointments_today = 0;
        Online_consultations_today = 0;
        list_of_speciality = {}
        speciality = []
        l = HospitalSpeciality.objects.filter(hospitalid=user.userid)
        for i in l:
            speciality.append(i.speciality)
            list_of_speciality[i.speciality] = 0
        list_of_doctors = Doctor.objects.filter(hospitalid=user.userid)
        P = 0;
        doctors_data = {}
        for i in list_of_doctors:
            l1 = []
            l2 = 0;
            # print(Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count())
            l2 = Appointments.objects.filter(appointment_date__month=dt.month).filter(
                doctoremail=i.doctorid.email).count()
            list_of_speciality[i.specialization] += l2
            p1 = HospitalSpeciality.objects.filter(speciality=i.specialization).filter(hospitalid=user.userid)
            if (len(p1) == 0):
                l1.append(0)
                l12 = Appointment_slots.objects.filter(doctorid=i).filter(date=dt)
                if (len(l12) > 0):
                    print(len(l12))
                    if (l12[0].available == True):
                        l1.append("Yes")
                    else:
                        l1.append("No")
                else:
                    l1.append("Yes")
                l1.append(0)

            else:
                for k1 in p1:
                    l1.append(l2)
                    l12 = Appointment_slots.objects.filter(doctorid=i).filter(date=dt)

                    if (len(l12) > 0):
                        if (l12[0].available == True):
                            l1.append("Yes")
                        else:
                            l1.append("No")
                    else:
                        l1.append("Yes")
                    l1.append(k1.price * l2)
            doctors_data[i] = l1
            appointments_this_month += l2
            appointments_today += Appointments.objects.filter(appointment_date=dt).filter(
                doctoremail=i.doctorid.email).count()
            Online_consultations_today += Appointments.objects.filter(appointment_date=dt).filter(
                mode_of_meeting="Online").filter(doctoremail=i.doctorid.email).count()
            k = Appointments.objects.filter(appointment_date__month=dt.month).filter(
                doctoremail=i.doctorid.email).aggregate(Sum('amount_paid'))
            if (k['amount_paid__sum'] != None):
                earning_this_month += k['amount_paid__sum']
            l23 = Appointments.objects.filter(appointment_date=dt).filter(doctoremail=i.doctorid.email)
            for i in l23:
                Appointments1.append(i)
        print(list_of_speciality)
        return render(request, "main_app/Admin_Dashboard.html",
                      context={"speciality": speciality, "list_of_Appointments": Appointments1,
                               "doctors_data": doctors_data,
                               "list_of_speciality": json.dumps(list(list_of_speciality.keys())),
                               "list_of_speciality_appointments": list(list_of_speciality.values()),
                               "Online_consultations_today": Online_consultations_today,
                               "appointments_this_month": appointments_this_month,
                               "earning_this_month": earning_this_month, "appointments_today": appointments_today})
    if(user.user_type=='Patient'):
        i=Patient.objects.get(patientid=user)
        User_Profile=i;
        list_of_Appointments = Appointments.objects.filter(patientemail=email).order_by('-appointment_date')
        return render(request, 'main_app/Profile.html',
                              context={"list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile})

    elif (user.user_type == 'Doctor'):
        User_Profile=Doctor.objects.get(doctorid=user.userid)
        l1=Appointment_slots.objects.filter(doctorid=user.userid).filter(date=datetime.date.today())
        if(len(l1)>0):
            available=l1[0].available
        list_of_Appointments =Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).order_by('-appointment_date')
        online_Appointments=Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).filter(mode_of_meeting="Online").count()
        no_of_Appointments=Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).count();
        no_of_Appointments_completed==Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).filter(~Q(Prescription='')).count();
        return render(request, 'main_app/Profile.html',
                      context={"available":available,"list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile,
                               "no_of_Appointments_completed": no_of_Appointments_completed,
                               "no_of_Appointments": no_of_Appointments,
                               "online_Appointments": online_Appointments})

    elif(user.user_type=="Testing Lab"):
        User_Profile=TestingLab.objects.get(tlabid=user.userid)
        list_of_Appointments = Appointments.objects.filter(TestingLabId=User_Profile).order_by('-appointment_date')
        no_of_test_appointments=[]
        l1=Appointment_slots.objects.filter(TestingLab=user.userid).filter(date=datetime.date.today())
        if(len(l1)>0):
            available=l1[0].available
        no_of_Appointments_completed=Appointments.objects.filter(TestingLabId=User_Profile).filter(appointment_date__month=dt.month).filter(~Q(Prescription='')).count();
        no_of_Appointments=Appointments.objects.filter(TestingLabId=User_Profile).filter(appointment_date__month=dt.month).count();
        tests=[]
        list_of_tests=TestPricing.objects.filter(tlabid=User_Profile)
        for i in list_of_tests:
            t1=Appointments.objects.filter(TestingLabId=User_Profile).filter(appointment_date__month=dt.month).filter(Speciality=i.testname).count();
            no_of_test_appointments.append(t1)
            tests.append(i.testname)
        return render(request, 'main_app/Profile.html',
                      context={"available":available,"dict_test": no_of_test_appointments, "Test_Names": json.dumps(tests),
                               "list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile,
                               "no_of_Appointments_completed": no_of_Appointments_completed,
                               "no_of_Appointments": no_of_Appointments})



def index(request):
    return render(request,'main_app/index.html')
def home(request):
    return render(request,'main_app/home.html')

def Hospitals(request):
    lis_of_countries = geo_plug.all_CountryNames()
    p=Hospital.objects.filter(verified="Yes")
    list_of_tests=list_of_medical_tests();
    list_of_speciality=get_specialities()
    return render(request,'main_app/Hospital_Selection.html',context={'list_of_countries':lis_of_countries,"list_of_hospitals":p,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})


def create_jwt_token():  # To create jwt token for zoom api
    start = int(time.time())
    end = start + 10

    Payload = {
        "aud": None,
        "iss": secret_settings.Api_Key,
        "exp": end,
        "iat": start
    }
    encoded = jwt.encode(Payload, secret_settings.Api_Secret, algorithm='HS256')
    return encoded

def create_zoom_meeting(date,time):
    url = "https://api.zoom.us/v2/users/"+secret_settings.email_host_user+"/meetings"
    password=random.randint(0,999999) #Password of Zoom meeting
    duration=30 # Duration of Zoom meeting
    #k=datetime.datetime.now()
    start_time=date+"T"+time # StartTime for zoom meeting
    print(start_time)
    data = {
        "topic": "Meet",
        "type": "2",
        "start_time": start_time,
        "duration": duration,
        "timezone": "Asia/Calcutta",
        "password": password,
        "agenda": "Online Consultation",
        "settings": {
            "join_before_host": True,
            "waiting_room": False
        }
    }
    data_json = json.dumps(data)
    encoded = create_jwt_token()
    encoded = encoded.decode('ASCII')
    headers = {
        "Authorization": "Bearer " + str(encoded), "Accept": "application/json", "content-type": "application/json"}
    response = requests.post(url, data=data_json, headers=headers)
    jsonResponse = response.json()
    return jsonResponse['join_url']
   # {'meeting_url': jsonResponse['join_url'], 'meeting_id': jsonResponse['id'],
    # 'meeting_password': jsonResponse['password']}


def list_of_states(request):
    list1 = geo_plug.all_Country_StateNames()[1:].split("},")
    states={}
    country=request.GET.get("country")
    for i in list1:
        k = i.split(":")
        header = re.sub("{", "", re.sub("\"", "", k[0])).strip()
        trailing = re.sub("{", "", re.sub("\"", "", k[1])).strip()
        trailing=re.sub("\'","",trailing)

        states[header] =trailing[1:len(trailing) - 1]
    for key, item in states.items():
        if (key == country):
            lis_of_states = item
    print(lis_of_states)
    return JsonResponse(data=lis_of_states,safe=False)

def list_of_city(request):
    state=request.GET.get("city")
    state=re.sub("\"","",state).strip()
    print(state)
    list_of_cities=[]
    city = geo_plug.all_State_CityNames(str(state))
    k = city.split(":")
    trailing =re.sub("\"", "", k[1])
    trailing=re.sub("}","",re.sub("\]","",re.sub("\[","",trailing))).strip()
    lis_of_cities = trailing[0:len(trailing)].split(",")
    #lis_of_cities=list(re.sub("\]","",re.sub("\'","",re.sub("\[","",str(lis_of_cities)))))
    for i in lis_of_cities:
        str1=i.replace("\\","")
        #print(str1)
        for key,value in replace_dictionary.items():
            if(str1.find(key)!=-1):
                str1=str1.replace(key,value)
        list_of_cities.append(str1)
    return JsonResponse(data=list_of_cities, safe=False)

def list_of_hospital(request):
    try:
        filter_type=request.POST.get("filter")
        lis_of_countries = geo_plug.all_CountryNames()
        list_of_speciality=get_specialities()
        list_of_tests=list_of_medical_tests()
        #print("ppp:",filter_type)
        filter1=''
        if(filter_type=='speciality'):
           speciality = request.POST['speciality']
           list_of_hospital=[]
           filter="Hospitals"
           k1=HospitalSpeciality.objects.filter(speciality=speciality)
           for i in k1:
               list_of_hospital.append(Hospital.objects.get(hospitalid=i.hospitalid))
           list_of_clinics=Doctor.objects.filter(specialization=speciality).filter(~Q(clinic_name=""))
           return render(request, "main_app/Hospital_Selection.html",
                          context={"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality,"list_of_doctors": list_of_clinics,"list_of_hospitals":list_of_hospital,"filter":filter,'list_of_countries':lis_of_countries,})
        elif(filter_type=='Test Name'):
            print("hello")
            testname=request.POST['Test_Name'];
            print(testname)
            p=[]
            k=TestPricing.objects.filter(testname=testname)
            for i in k:
                p.append(TestingLab.objects.get(tlabid=i.tlabid))
            filter="Testing_Lab"
            list_of_tests = list_of_medical_tests();
            return render(request, "main_app/Hospital_Selection.html",
                          context={"list_of_testing_labs": p, "filter": filter,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality,'list_of_countries': lis_of_countries})

        elif(filter_type=='Hospitals'):
            p = Hospital.objects.all()
            filter="Hospitals"
        elif(filter_type=='Testing_Labs'):
            p=TestingLab.objects.all()
            filter="Testing_Labs"
            return render(request, "main_app/Hospital_Selection.html",
                          context={"list_of_testing_labs": p, "filter": filter,
                                   'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        elif(filter_type=='Clinics'):
            p=Doctor.objects.filter(~Q(clinic_name=''))
            filter="Clinics"
            print(p)
            return render(request, "main_app/Hospital_Selection.html",
                          context={"list_of_doctors": p, "filter": filter,
                                   'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})

        if(filter_type=='Location'):
            Country=request.POST.get("country")
            City=request.POST.get("city")
            State=request.POST.get("state")
            p=Hospital.objects.filter(country=Country).filter(city=City).filter(verified="Yes")
            filter="Hospital"
        elif (filter_type == 'Doctor_Name'):
            p = []
            search_value = request.POST.get("search_values")
            for i in Doctor.objects.all():
                if (i.doctorid.name == search_value):
                    p.append(i)
                    break;
            #print(p,search_value)
            return render(request, "main_app/Hospital_Selection.html",
                          context={"list_of_doctors": p,"filter":"Doctor", 'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        elif(filter_type=='Hospital_Name'):
            p=[]
            search_value=request.POST.get("search_values")
            for i in Hospital.objects.all():
                if(i.hospitalid.name==search_value):
                    p.append(i)
                    filter="Hospital"
                    break;

        elif(filter_type=='Testing_Lab'):
            search_value = request.POST.get("search_values")
            p=[]
            for i in TestingLab.objects.all():
                if(i.tlabid.name==search_value):
                    p.append(i);
                    filter="Testing_Lab"
                    return render(request, "main_app/Hospital_Selection.html",
                                  context={"list_of_testing_labs": p, "filter": "Doctor",
                                           'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        return render(request,"main_app/Hospital_Selection.html",context={"list_of_hospitals":p,"filter":filter,'list_of_countries':lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})

    except:
        return redirect("/Hospital_Selection/")

def Selected_Service_Provider(request,user_id):
    user=UserDetails.objects.get(userid=user_id)
    request.session['user_type_Id']=user_id
    print(user.user_type)
    if(user.user_type=="Hospital"):
        p = Hospital.objects.get(hospitalid=user_id)
        k=HospitalSpeciality.objects.filter(hospitalid=p)
        Specialities=[]
        for i in k:
            Specialities.append(i.speciality)
        dict1={}
        poke = pd.read_csv("main_app/static/Specialities_Images.csv")
        list1 =poke['Speciality'].tolist()
        list2=poke['Speciality_Image'].tolist()
        #print(list1,list2)
        for i in Specialities:
            dict2={}
            if i in list1:
                l0=HospitalSpeciality.objects.filter(speciality=i).filter(hospitalid=user_id)
                dict2[list2[list1.index(i)]]=l0[0].price
                dict1[i]=dict2
        return render(request,"main_app/Dashboard.html",context={"Hospital_Details":p,"specialities":dict1})
    elif(user.user_type=="Testing Lab"):
        p = TestingLab.objects.get(tlabid=user_id)
        k = TestPricing.objects.filter(tlabid=user_id)
        Tests = []
        for i in k:
            Tests.append(i)
        return render(request, "main_app/Dashboard.html", context={"Testing_Lab_Details": p, "specialities": Tests})
def Book_Appointment(request):
    return render(request,"main_app/Book_Appointment.html",context={"Doctor":replace_dictionary,"specialities":Specialities,"facilities":Facilities})

def Add_Prescription(request):
    Patient_Email=request.POST['Email']
    Appointment_Id=request.POST['id']

    return render(request,"main_app/Prescription.html",context={"Patient_Email":Patient_Email,'Appointment_Id':Appointment_Id})

def submit_Prescription(request):
    email = request.POST['Email']
    Appointment_Id=request.POST['Appointment_Id']
    dict={}
    prescription = request.FILES['prescription']
    #b1 = Patient.objects.filter(doctorid=doctor_details).filter(date=request.session['date'])
    b1=Appointments.objects.get(appointmentid=int(Appointment_Id))
    b1.Prescription=prescription
    b1.save()
    return redirect("/profile")
    #return render(request,"main_app/Profile.html",context={"list_of_Appointments":dict})
def Appointment_Details_Submission(request):
        dt=datetime.datetime.now()
        a1=Appointments()
        mode=request.POST['mode']
        doctorid=request.POST['doctorid']
        email=request.session['email']
        i=UserDetails.objects.get(email=email)
        a1.patientname=i.name
        a1.patientemail=i.email
        #a1.Speciality=request.session['speciality']
        i=Doctor.objects.get(doctorid=int(doctorid))
        a1.doctoremail=i.doctorid.email
        doctor_details=i
        hospital_id=i.hospitalid
        speciality=i.specialization
        a1.Speciality=speciality
        l1=HospitalSpeciality.objects.filter(hospitalid=hospital_id).filter(speciality=speciality)
        a1.amount_paid =l1[0].price
        try:
            #if(request.POST['date']!=None):
            a1.appointment_date=request.POST['date']
        except:
            a1.appointment_date=request.session["date"]
        d=a1.appointment_date

        t = Appointment_slots.objects.filter(doctorid=doctorid).filter(date=a1.appointment_date)
        no_of_slots_booked_already=0
        lis=d.split('-')
        if len(t) > 0 :
                no_of_slots_booked_already=t[0].Slots_Booked
                if(no_of_slots_booked_already>14 or t[0].available==False):
                    print(t[0].available)
                    messages.info(request,"Doctor not availaible on this date")
                    return redirect('/Hospital_Selection')
                elif no_of_slots_booked_already%2==0:
                    k=9+no_of_slots_booked_already//2
                    a1.appointment_time=datetime.time(k,0,0)
                    t1=str(k)+":00"+":00"
                else:
                    k = 9 + no_of_slots_booked_already // 2
                    a1.appointment_time = datetime.time(k,30,0)
                    t1=str(k)+":30"+":00"
        else:
                a1.appointment_time =datetime.time(9,0,0)
                t1 = "09:00:00"


        if (mode == 'Online'):
           date1=a1.appointment_date
           a1.meeting_url=create_zoom_meeting(date1,t1)
           a1.mode_of_meeting = mode
        else:
            a1.mode_of_meeting = mode
        a1.save()
        b1=Appointment_slots.objects.filter(doctorid=doctor_details).filter(date=a1.appointment_date)
        if len(b1)>0:
            b1.update(Slots_Booked=no_of_slots_booked_already+1)
        else:
            b1=Appointment_slots()
            b1.doctorid=doctor_details
            b1.date=a1.appointment_date
            b1.Slots_Booked=1
            b1.save()
        return render(request,"main_app/Receipt.html",context={"Appointment_Details":a1})
    #except:
    #    return redirect("/Doctor/")

def select_speciality(request):
    user_id=request.session['user_type_Id']
    user = UserDetails.objects.get(userid=user_id)
    if(user.user_type=="Hospital"):
        p = Hospital.objects.get(hospitalid=user_id)
        k = HospitalSpeciality.objects.filter(hospitalid=p)
        Specialities = []
        for i in k:
            Specialities.append(i.speciality)
        return render(request,"main_app/List_Of_Speciality.html",context={"specialities":Specialities,"Hospital_Details":p})
    elif(user.user_type=="Testing Lab"):
        p = TestingLab.objects.get(tlabid=user_id)
        k = TestPricing.objects.filter(tlabid=user_id)
        Tests = []
        for i in k:
            Tests.append(i.testname)
        return render(request, "main_app/List_Of_Speciality.html", context={"Testing_Lab_Details": p, "specialities": Tests})
def book_appointment1(request,speciality):
    user=UserDetails.objects.get(userid=request.session['user_type_Id'])
    request.session['speciality'] = speciality
    if(user.user_type=="Hospital" or user.user_type=="Clinic"):
        p=Doctor.objects.filter(specialization=speciality).filter(hospitalid=request.session['user_type_Id']).filter(verified="Yes")
        #t=Appointment_slots. vfv,mflv.filter(date=request.session['date']).filter(Slots_Booked < 16)
        #list_of_doctors={}
        list_of_doctors=[]
        for i in p:
            t=Appointment_slots.objects.filter(doctorid=i).filter(date=request.session['date'])
            print(len(t))
            if len(t)==0:
                list_of_doctors.append(i)
                 #list_of_doctors[i]=time_slots.split(",")
            else:
                #print(t[0].Slots_Booked)
                print("availabel",t[0].available)
                if(t[0].Slots_Booked < 16 and t[0].available==True):
                    list_of_doctors.append(i)
                    #list_of_doctors[i] = time_slots.split(",")

        k = Hospital.objects.get(hospitalid=user.userid)

        return render(request, "main_app/Select_Doctor.html", context={"list_of_Doctors": list_of_doctors,"Hospital_Details":k})
    elif(user.user_type == "Testing Lab"):
        t=Appointment_slots.objects.filter(TestingLab=user.userid).filter(date=request.session['date'])
        k=TestPricing.objects.filter(tlabid=user.userid)
        dt=datetime.datetime.now()
        d=request.session['date']
        lis = d.split('-')
        if(len(t)>0):
            if(t[0].Slots_Booked >14 or t[0].available==False):
                p = TestingLab.objects.get(tlabid=user.userid)
                Tests = []
                for i in k:
                    Tests.append(i.testname)
                messages.info(request, "No Appointment Available on this date")
                return render(request, "main_app/List_Of_Speciality.html",
                              context={"Testing_Lab_Details": p, "specialities": Tests})
        elif(len(t)==0 or (t[0].Slots_Booked <15 and t[0].available==True)):
                a1 = Appointments()
                mode = "Remote"
                TestingLabId=request.session['user_type_Id']
                p1=UserDetails.objects.get(email=request.session['email'])
                a1.patientname = p1.name
                a1.patientemail = p1.email
                a1.Speciality = request.session['speciality']
                l1 = TestPricing.objects.filter(tlabid=user.userid).filter(
                    testname=request.session['speciality'])
                a1.amount_paid = l1[0].price
                a1.TestingLabId=TestingLab.objects.get(tlabid=user.userid)
                try:
                   a1.appointment_date = request.POST['date']
                except:
                    a1.appointment_date = request.session["date"]
                t = Appointment_slots.objects.filter(TestingLab=user.userid).filter(date=request.session['date'])
                no_of_slots_booked_already = 0
                if len(t) > 0:
                        no_of_slots_booked_already = t[0].Slots_Booked
                        if no_of_slots_booked_already % 2 == 0:
                            k = 9 + no_of_slots_booked_already // 2
                            a1.appointment_time = datetime.time(k, 0, 0)
                        else:
                            k = 9 + no_of_slots_booked_already // 2
                            a1.appointment_time = datetime.time(k, 30, 0)

                else:
                        a1.appointment_time = datetime.time(9, 0, 0)

                a1.mode_of_meeting = "Remote"
                a1.save()
                b1 = Appointment_slots.objects.filter(TestingLab=user.userid).filter(date=request.session['date'])
                if len(b1) > 0:
                    b1.update(Slots_Booked=no_of_slots_booked_already + 1)
                else:
                    b1 = Appointment_slots()
                    b1.TestingLab = TestingLab.objects.get(tlabid=user.userid)
                    b1.date = request.session["date"]
                    b1.Slots_Booked = 1
                    b1.save()
        return render(request, "main_app/Receipt.html", context={"Appointment_Details": a1})

def chosen_date(request):
    request.session['date']=request.GET.get("date")
    print(request.GET.get("date"))
    return JsonResponse(request.session['date'],safe=False)

def search_appointments(request):
    try:
        no_of_Appointments_completed = 0;
        no_of_Appointments = 0;
        dt=datetime.datetime.now();
        email = request.session['email']
        filter_type=request.POST['filter']
        search_values=request.POST['search_values']
        dict = {}
        user=UserDetails.objects.get(email=email)
        if (user.user_type == 'Patient'):
            User_Profile=Patient.objects.get(patientid=user.userid)
            if(filter_type=='Date'):
                list_of_Appointments = Appointments.objects.filter(patientemail=email).filter(appointment_date=search_values)
                print(list_of_Appointments)
                dict=appoin(list_of_Appointments)
            else:
                lis_of_doctors=UserDetails.objects.filter(user_type="Doctor").filter(name__iexact=search_values)
                for i in lis_of_doctors:
                    list_of_Appointments=Appointments.objects.filter(patientemail=email).filter(doctoremail__iexact=i.email)
                    for j in list_of_Appointments:
                        if (j.Prescription != ""):
                            dict[j] = j
                        else:
                            dict[j] = "Upload Prescription"

            return render(request, 'main_app/Profile.html',
                          context={"list_of_Appointments": dict, "User_Details": User_Profile})

        elif (user.user_type == 'Doctor'):
                i=Doctor.objects.get(doctorid=user)
                User_Profile = i
                l1 = Appointment_slots.objects.filter(doctorid=user.userid).filter(date=datetime.date.today())
                if (len(l1) > 0):
                    available = l1[0].available
                online_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                    appointment_date__month=dt.month).filter(mode_of_meeting="Online").count()
                no_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                    appointment_date__month=dt.month).count();
                no_of_Appointments_completed == Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                    appointment_date__month=dt.month).filter(~Q(Prescription='')).count();
                if (filter_type == 'Date'):
                        list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter( appointment_date=search_values)
                else:
                        list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                            patientname__iexact=search_values)
                return render(request, 'main_app/Profile.html',
                              context={"available": available, "list_of_Appointments": appoin(list_of_Appointments),
                                       "User_Details": User_Profile,
                                       "no_of_Appointments_completed": no_of_Appointments_completed,
                                       "no_of_Appointments": no_of_Appointments,
                                       "online_Appointments": online_Appointments})

        # print(p)
        elif(user.user_type=="Testing Lab"):
            User_Profile=TestingLab.objects.get(tlabid=user.userid)
            if (filter_type == 'Date'):
                    list_of_Appointments = Appointments.objects.filter(TestingLabId=user.userid).filter(
                appointment_date=search_values)
            else:
                list_of_Appointments = Appointments.objects.filter(TestingLabId=user.userid).filter(
                patientname__iexact=search_values)
            no_of_test_appointments = []
            l1 = Appointment_slots.objects.filter(TestingLab=user.userid).filter(date=datetime.date.today())
            if (len(l1) > 0):
                available = l1[0].available
            no_of_Appointments_completed = Appointments.objects.filter(TestingLabId=User_Profile).filter(
                appointment_date__month=dt.month).filter(~Q(Prescription='')).count();
            no_of_Appointments = Appointments.objects.filter(TestingLabId=User_Profile).filter(
                appointment_date__month=dt.month).count();
            tests = []
            list_of_tests = TestPricing.objects.filter(tlabid=User_Profile)
            for i in list_of_tests:
                t1 = Appointments.objects.filter(TestingLabId=User_Profile).filter(
                    appointment_date__month=dt.month).filter(Speciality=i.testname).count();
                no_of_test_appointments.append(t1)
                tests.append(i.testname)
            return render(request, 'main_app/Profile.html',
                          context={"available": available, "dict_test": no_of_test_appointments,
                                   "Test_Names": json.dumps(tests),
                                   "list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile,
                                   "no_of_Appointments_completed": no_of_Appointments_completed,
                                   "no_of_Appointments": no_of_Appointments})
            # print(p)

    except:
        return redirect('/profile')
def Appointment_Details(request,appointment_id):
    Appointment_Details1=Appointments.objects.get(appointmentid=appointment_id)
    return render(request,'main_app/Receipt.html',context={'Appointment_Details':Appointment_Details1})

def admin(request):
    dt = datetime.datetime.today()
    Appointments1=[]
    appointments_this_month=0;
    earning_this_month=0;
    appointments_today =0;
    Online_consultations_today=0;
    list_of_speciality={}
    speciality=[]
    l = HospitalSpeciality.objects.filter(hospitalid=16)
    for i in l:
        speciality.append(i.speciality)
        list_of_speciality[i.speciality]=0
    list_of_doctors=Doctor.objects.filter(hospitalid=16)
    P=0;
    doctors_data={}
    for i in list_of_doctors:
        l1=[]
        l2=0;
        #print(Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count())
        l2 = Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count()
        list_of_speciality[i.specialization]+=l2
        p1=HospitalSpeciality.objects.filter(speciality=i.specialization).filter(hospitalid=16)
        if(len(p1)==0):
            l1.append(0)
            l12 = Appointment_slots.objects.filter(doctorid=i).filter(date=dt)
            if (len(l12) > 0):
                print(len(l12))
                if (l12[0].available == True):
                    l1.append("Yes")
                else:
                    l1.append("No")
            else:
                l1.append("Yes")
            l1.append(0)

        else:
            for k1 in p1:
                l1.append(l2)
                l12=Appointment_slots.objects.filter(doctorid=i).filter(date=dt)

                if(len(l12)>0):
                    if(l12[0].available==True):
                        l1.append("Yes")
                    else:
                        l1.append("No")
                else:
                    l1.append("Yes")
                l1.append(k1.price * l2)
        doctors_data[i] = l1
        appointments_this_month+=l2
        appointments_today+=Appointments.objects.filter(appointment_date=dt).filter(doctoremail=i.doctorid.email).count()
        Online_consultations_today += Appointments.objects.filter(appointment_date=dt).filter(mode_of_meeting="Online").filter(doctoremail=i.doctorid.email).count()
        k=Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).aggregate(Sum('amount_paid'))
        if(k['amount_paid__sum']!=None):
            earning_this_month+=k['amount_paid__sum']
        l23 = Appointments.objects.filter(appointment_date=dt).filter(doctoremail=i.doctorid.email)
        for i in l23:
            Appointments1.append(i)
    print(list_of_speciality)
    return render(request, "main_app/Admin_Dashboard.html",context={"speciality":speciality,"list_of_Appointments":Appointments1,"doctors_data":doctors_data,"list_of_speciality":json.dumps(list(list_of_speciality.keys())),"list_of_speciality_appointments":list(list_of_speciality.values()),"Online_consultations_today":Online_consultations_today,"appointments_this_month":appointments_this_month,"earning_this_month":earning_this_month,"appointments_today":appointments_today})

def admin_search_appointments(request):
    email=request.session['email']
    user = UserDetails.objects.get(email=email)
    dt = datetime.datetime.today()
    Appointments1 = []
    appointments_this_month = 0;
    earning_this_month = 0;
    appointments_today = 0;
    Online_consultations_today = 0;
    list_of_speciality = {}
    speciality = []
    l = HospitalSpeciality.objects.filter(hospitalid=user.userid)
    for i in l:
        speciality.append(i.speciality)
        list_of_speciality[i.speciality] = 0
    list_of_doctors = Doctor.objects.filter(hospitalid=user.userid)
    P = 0;
    doctors_data = {}
    for i in list_of_doctors:
        l1 = []
        l2 = 0;
        # print(Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count())
        l2 = Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count()
        list_of_speciality[i.specialization] += l2
        p1 = HospitalSpeciality.objects.filter(speciality=i.specialization).filter(hospitalid=user.userid)
        if (len(p1) == 0):
            l1.append(0)
            l12 = Appointment_slots.objects.filter(doctorid=i).filter(date=dt)
            if (len(l12) > 0):
                print(len(l12))
                if (l12[0].available == True):
                    l1.append("Yes")
                else:
                    l1.append("No")
            else:
                l1.append("Yes")
            l1.append(0)

        else:
            for k1 in p1:
                l1.append(l2)
                l12 = Appointment_slots.objects.filter(doctorid=i).filter(date=dt)

                if (len(l12) > 0):
                    if (l12[0].available == True):
                        l1.append("Yes")
                    else:
                        l1.append("No")
                else:
                    l1.append("Yes")
                l1.append(k1.price * l2)
        doctors_data[i] = l1
        appointments_this_month += l2
        appointments_today += Appointments.objects.filter(appointment_date=dt).filter(
            doctoremail=i.doctorid.email).count()
        Online_consultations_today += Appointments.objects.filter(appointment_date=dt).filter(
            mode_of_meeting="Online").filter(doctoremail=i.doctorid.email).count()
        k = Appointments.objects.filter(appointment_date__month=dt.month).filter(
            doctoremail=i.doctorid.email).aggregate(Sum('amount_paid'))
        if (k['amount_paid__sum'] != None):
            earning_this_month += k['amount_paid__sum']
        l23 = Appointments.objects.filter(appointment_date=dt).filter(doctoremail=i.doctorid.email)
        for i in l23:
            Appointments1.append(i)
    print(list_of_speciality)
    #email = request.session['email']
    filter_type = request.POST['filter']
    if (filter_type == "speciality"):
        search_values = request.POST['search_values1']
    else:
        search_values = request.POST['search_values']

    print(search_values)
    for i in list_of_doctors:
            print(i.doctorid.email)
            if (filter_type == "Date"):
                    p1=Appointments.objects.filter(appointment_date=search_values).filter(doctoremail=i.doctorid.email)
                    for j in p1:
                        Appointments1.append(j)
            elif (filter_type == "Doctor Name"):
                doctor = UserDetails.objects.filter(name__iexact=search_values).filter(user_type="Doctor")
                for j in doctor:
                    Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(doctoremail=j.email)
                break;
            elif(filter_type=="Patient"):
                Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(patientname__iexact=search_values)
                break;
            elif(filter_type=="speciality"):
                Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(
                    Speciality=search_values)
                break;
    print(Appointments1)
    return render(request, "main_app/Admin_Dashboard.html",
                  context={"speciality":speciality,"list_of_Appointments": Appointments1, "doctors_data": doctors_data,
                           "list_of_speciality": json.dumps(list(list_of_speciality.keys())),
                           "list_of_speciality_appointments": list(list_of_speciality.values()),
                           "Online_consultations_today": Online_consultations_today,
                           "appointments_this_month": appointments_this_month, "earning_this_month": earning_this_month,
                           "appointments_today": appointments_today})


def availablity(request):
    user = UserDetails.objects.get(email=request.session['email'])
    start=request.POST['start'].split('-')
    end=request.POST['end'].split('-')
    start1=datetime.datetime(int(start[0]),int(start[1]),int(start[2]))
    end1=datetime.datetime(int(end[0]),int(end[1]),int(end[2]))
    date=start1
    list_of_appointments = []
    while(date<=end1):
        print(date.date())
        date1=date.date()

        if(user.user_type=="Testing Lab"):
            tester=TestingLab.objects.get(tlabid=user.userid)
            l2 = Appointments.objects.filter(appointment_date=date1).filter(TestingLabId=tester)
            p1=Appointment_slots.objects.filter(TestingLab=user.userid).filter(date=date1)
            if(len(p1)>0):
                a1=p1[0]
            else:
                a1 = Appointment_slots()
            a1.TestingLab=tester
            a1.available=False
            a1.date=date
            a1.Slots_Booked=0
            a1.save()
            for i in l2:
                list_of_appointments.append(i)
        elif(user.user_type=="Doctor"):
            doctor = Doctor.objects.get(doctorid=user.userid)
            l2 = Appointments.objects.filter(appointment_date=date1).filter(doctoremail=user.email)
            p1 = Appointment_slots.objects.filter(doctorid=user.userid).filter(date=date1)
            if (len(p1) > 0):
                a1 = p1[0]
            else:
                a1 = Appointment_slots()
            a1.doctorid = doctor
            a1.available = False
            a1.date = date
            a1.Slots_Booked = 0
            a1.save()
            for i in l2:
                list_of_appointments.append(i)
        date += datetime.timedelta(days=1)
    for i in list_of_appointments:
            i.delete();
            template = render_to_string('main_app/email_template.html',
            {
            'name': i.patientname,
            'user_type_name': user.user_type,
            'appointment_date':str(i.appointment_date.year)+'-'+str(i.appointment_date.month)+'-'+str(i.appointment_date.day),
            'fee': i.amount_paid,
             'domain': '127.0.0.1:8000',
            })
            email = EmailMessage(
                'Update relating to Appointment',
                template,
                settings.EMAIL_HOST_USER,
                [i.patientemail],
            )
            email.fail_silently = False
            email.send()
    return redirect("/profile")