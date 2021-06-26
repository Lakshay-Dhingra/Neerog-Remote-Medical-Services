import time
from django.contrib.auth import authenticate
from django.core.mail import send_mail, EmailMessage
from django.db.models import Sum, Avg
from django.template.loader import render_to_string
from .models import *;
from .medical_tests import *;
from .location import *;
from django.contrib import messages
import requests
from geopy.geocoders import Nominatim
import re
import json
import pandas as pd
from django.http import HttpResponse, JsonResponse
#from geosky import geo_plug # library for geolocation
import datetime
import jwt
from django.shortcuts import render, redirect
from Neerog import secret_settings,settings
import random
from .medical_speciality import get_specialities
from .medical_tests import list_of_medical_tests
from . import search_data, domain

replace_dictionary={"u0101":"a","u012b":"i","u016b":"u","u0100":"A","u016a":"u"}

def search(request):
    search = request.GET['search']
    result_list = search_data.searchResults(search)
    context = {'search':search, 'result_list':result_list}
    return render(request,"main_app/display_search.html",context)

# Verification of the user certificate
def verify_certificate(request):
    try:
        id=int(request.GET['id'])
        user = UserDetails.objects.get(email=request.session['email'])
        if (user.user_type == 'Moderator'):
            user = UserDetails.objects.get(userid=id)
            if (user.user_type == 'Hospital'):
                p = Hospital.objects.get(hospitalid=user)
                p.verified = "Yes"
                p.save()
            elif (user.user_type == 'Doctor'):
                p = Doctor.objects.get(doctorid=user)
                p.verified = "Yes"
                p.save()
            else:
                p = TestingLab.objects.get(tlabid=user)
                p.verified = "Yes"
                p.save()
            p = dict()
            if (len(Hospital.objects.filter(verified="No")) > 0):
                p['Hospital'] = Hospital.objects.filter(verified="No")
            if (len(Doctor.objects.filter(verified="No")) > 0):
                p['Doctor'] = Doctor.objects.filter(verified="No")
            if (len(TestingLab.objects.filter(verified="No")) > 0):
                p['Testing_Lab'] = TestingLab.objects.filter(verified="No")
            return render(request, "main_app/Verify_Certificate.html", context={'list_of_certificates': p})
        else:
            messages.info(request, "You Can't Access This Page!")
            return redirect("/")
    except:
        messages.info(request, "You Can't Access This Page!")
        return redirect("/")

def appoin(list_of_Appointments):
    dict={}
    no_of_appointment_completed=0
    for i in list_of_Appointments:
        if (i.Prescription!=""):
            dict[i] = i
        else:
            p = i.appointment_time
            p1 = i.appointment_date
            dt = datetime.datetime.now()
            dt1 = datetime.datetime(int(p1.strftime("%Y")), int(p1.strftime("%m")), int(p1.strftime("%d")),
                                    int(p.strftime("%H")), int(p.strftime("%M")), int(p.strftime("%S")))
            k = dt-dt1
            # print(k.total_seconds())
            if (k.total_seconds() > 1800):
                dict[i] = "Upload Prescription review"
            else:
                dict[i] = "Upload Prescription"


    return dict

def profile(request,id):
    try:
        dt = datetime.datetime.today()
        try:
            email=request.session['email']
        except:
            messages.info("Please Login/Register")
            return redirect("/accounts/signin");
        no_of_Appointments_completed=0;
        no_of_Appointments=0;
        available=True;
        user23=UserDetails.objects.get(email=email)
        user=UserDetails.objects.get(userid=id)
        email=user.email
        if(user.user_type=='Hospital'):
            if(id!=user23.userid):
               #messages.info(request,"You are not authorised to access this page")
               k7="/dashboard/"+str(user23.userid)
               return redirect(k7);
            else:
                dt = datetime.datetime.today()
                Appointments1 = []
                appointments_this_month = 0;
                earning_this_month = 0;
                appointments_today = 0;
                min=0;
                max=0;
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
                    user1 = UserDetails.objects.get(userid=i.doctorid.userid)
                    # print(Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count())
                    l2 = Appointments.objects.filter(appointment_date__month=dt.month).filter(
                        doctoremail=i.doctorid.email).count()
                    if(l2<min):
                        min=l2
                    if(l2>max):
                        max=l2;
                    list_of_speciality[i.specialization] += l2
                    p1 = HospitalSpeciality.objects.filter(speciality=i.specialization).filter(hospitalid=user.userid)
                    if (len(p1) == 0):
                        l1.append(0)
                        l12 = Appointment_Timings.objects.filter(service_provider_id=user1.userid).filter(date=dt)
                        if (len(l12) > 0):
                            #print(len(l12))
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
                            l12 = Appointment_Timings.objects.filter(service_provider_id=user1.userid).filter(date=dt)
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
                    if(min>2):
                        min-1;
                #print(list_of_speciality)
                return render(request, "main_app/Hospital_Dashboard.html",
                              context={"speciality": speciality, "list_of_Appointments": Appointments1,"min":min,"max":max+20,
                                       "doctors_data": doctors_data,"hospitalid":id,
                                       "list_of_speciality": json.dumps(list(list_of_speciality.keys())),
                                       "list_of_speciality_appointments": list(list_of_speciality.values()),
                                       "Online_consultations_today": Online_consultations_today,
                                       "appointments_this_month": appointments_this_month,
                                       "earning_this_month": earning_this_month,"filter_type":"Date","appointments_today": appointments_today})
        if(user.user_type=='Patient'):
            li=[1,2,3,4,5]
            if (id != user23.userid):
                # messages.info(request,"You are not authorised to access this page")
                k7 = "/dashboard/" + str(user23.userid)
                return redirect(k7);
            else:
                i=Patient.objects.get(patientid=user)
                User_Profile=i;
                list_of_Appointments = Appointments.objects.filter(patientemail=email).order_by('-appointment_date')
                return render(request, 'main_app/Doctor_Testing_Lab_Dashboard.html',
                                      context={"dummy":li,"filter_type":"Date","list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile})

        elif (user.user_type == 'Doctor'):
            if(user23.user_type=="Hospital"):
                doctor=Doctor.objects.get(doctorid=id)
                if(doctor.hospitalid.hospitalid.userid!=user23.userid):
                    messages.info(request, "You are not authorised to access this page")
                    k7="/dashboard/"+str(user23.userid)
                    return redirect(k7);
                else:
                    User_Profile = Doctor.objects.get(doctorid=user.userid)
                    l1 = Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(
                        date=datetime.date.today())
                    available = True
                    if (len(l1) > 0):
                        available = l1[0].available
                    list_of_Appointments = Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).order_by(
                        '-appointment_date')
                    online_Appointments = Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(
                        appointment_date__month=dt.month).filter(mode_of_meeting="Online").count()
                    no_of_Appointments = Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(
                        appointment_date__month=dt.month).count();
                    no_of_Appointments_completed = Appointments.objects.filter(
                        doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).exclude(
                        Prescription='').count();
                    return render(request, 'main_app/Doctor_Testing_Lab_Dashboard.html',
                                  context={"available": available, "list_of_Appointments": appoin(list_of_Appointments),
                                           "User_Details": User_Profile,
                                           "no_of_Appointments_completed": no_of_Appointments_completed,
                                           "no_of_Appointments": no_of_Appointments,
                                           "online_Appointments": online_Appointments, "filter_type": "Date"})
            else:
                if (id != user23.userid):
                    # messages.info(request,"You are not authorised to access this page")
                    k7 = "/dashboard/" + str(user23.userid)
                    return redirect(k7);
                else:
                    User_Profile=Doctor.objects.get(doctorid=user.userid)
                    l1=Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=datetime.date.today())
                    available=True
                    if(len(l1)>0):
                        available=l1[0].available
                    list_of_Appointments =Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).order_by('-appointment_date')
                    online_Appointments=Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).filter(mode_of_meeting="Online").count()
                    no_of_Appointments=Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).count();
                    no_of_Appointments_completed=Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).exclude(Prescription='').count();
                    return render(request, 'main_app/Doctor_Testing_Lab_Dashboard.html',
                                  context={"available":available,"list_of_Appointments":appoin(list_of_Appointments) , "User_Details": User_Profile,
                                           "no_of_Appointments_completed":no_of_Appointments_completed,
                                           "no_of_Appointments": no_of_Appointments,
                                           "online_Appointments": online_Appointments,"filter_type":"Date"})

        elif(user.user_type=="Testing Lab"):
            if (id != user23.userid):
                # messages.info(request,"You are not authorised to access this page")
                k7 = "/dashboard/" + str(user23.userid)
                return redirect(k7);
            else:
                earning_this_month=0
                User_Profile=TestingLab.objects.get(tlabid=user.userid)
                list_of_Appointments = Appointments.objects.filter(TestingLabId=User_Profile).order_by('-appointment_date')
                no_of_test_appointments=[]
                available=True
                l1=Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=datetime.date.today())
                if(len(l1)>0):
                    available=l1[0].available
                no_of_Appointments_completed=Appointments.objects.filter(TestingLabId=User_Profile).filter(appointment_date__month=dt.month).exclude(Prescription='').count();
                no_of_Appointments=Appointments.objects.filter(TestingLabId=User_Profile).filter(appointment_date__month=dt.month).count();
                k = Appointments.objects.filter(appointment_date__month=dt.month).filter(
                    TestingLabId=User_Profile).aggregate(Sum('amount_paid'))
                if (k['amount_paid__sum'] != None):
                    earning_this_month = k['amount_paid__sum']
                tests=[]
                list_of_tests=TestPricing.objects.filter(tlabid=User_Profile)
                max1=0;min1=0;
                for i in list_of_tests:
                    t1=Appointments.objects.filter(TestingLabId=User_Profile).filter(appointment_date__month=dt.month).filter(Speciality=i.testname).count();
                    no_of_test_appointments.append(t1)
                    if(t1<min1):
                        min1=t1
                    if(t1>max1):
                        max1=t1;
                    tests.append(i.testname)
                if (min1 > 2):
                    min1 - 1;
                return render(request, 'main_app/Doctor_Testing_Lab_Dashboard.html',
                              context={"min":min1,"max":max1+20,"earning_this_month": earning_this_month,"available":available,"dict_test": no_of_test_appointments, "Test_Names": json.dumps(tests),
                                       "list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile,
                                       "no_of_Appointments_completed": no_of_Appointments_completed,
                                       "no_of_Appointments": no_of_Appointments,"filter_type":"Date"})
        elif (user.user_type == 'Moderator'):
            if (id != user23.userid):
                # messages.info(request,"You are not authorised to access this page")
                k7 = "/dashboard/" + str(user23.userid)
                return redirect(k7);
            else:
                p = dict()
                if(len(Hospital.objects.filter(verified="No"))>0):
                    p['Hospital'] =Hospital.objects.filter(verified="No")
                if (len(Doctor.objects.filter(verified="No")) > 0):
                    p['Doctor'] = Doctor.objects.filter(verified="No")
                if (len(TestingLab.objects.filter(verified="No")) > 0):
                    p['Testing_Lab'] = TestingLab.objects.filter(verified="No")

                return render(request, "main_app/Verify_Certificate.html", context={'list_of_certificates': p})
    except:
        return redirect("/accounts/signup/redirect/")


def index(request):
    return render(request,'main_app/index.html')

def Hospitals(request):
    lis_of_countries = geo_plug.all_CountryNames()
    tests=getTests();
    list_of_tests=[]
    for i in tests:
        list_of_tests.extend(i.testlist)
    list_of_speciality=get_specialities()
    list_of_doctors={}
    try:
        city=request.session['city'].strip()
        state=request.session['state'].strip()
        country=request.session['country'].strip()
        location=city+','+state+','+country
        list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
        list_of_testing_labs=TestingLab.objects.filter(verified="Yes").filter(country=country).filter(city=city)
        p=Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city).exclude(clinic_name='')
        for i in p:
            list_of_doctors[i] = i.clinic_fee

    except:
        try:
            user=UserDetails.objects.get(email=request.session['email'])
            if(user.user_type=='Patient'):
                d1=Patient.objects.get(patientid=user.userid)
                list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city)
                list_of_testing_labs = TestingLab.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city)
                p = Doctor.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city).exclude(
                    clinic_name='')
                for i in p:
                    list_of_doctors[i] = i.clinic_fee
                location = d1.city + ',' + d1.state + ',' + d1.country
                request.session['country']=d1.country.strip()
                request.session['city'] = d1.city.strip()
                request.session['state'] = d1.state.strip()
            elif(user.user_type == 'Doctor'):
                d1 = Doctor.objects.get(doctorid=user.userid)
                list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city)
                list_of_testing_labs = TestingLab.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city)
                p = Doctor.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city).exclude(
                    clinic_name='')
                for i in p:
                    list_of_doctors[i] = i.clinic_fee
                location = d1.city + ',' + d1.state + ',' + d1.country
                request.session['country'] = d1.country.strip()
                request.session['city'] = d1.city.strip()
                request.session['state'] = d1.state.strip()

            elif (user.user_type == 'Testing Lab'):
                d1 = TestingLab.objects.get(tlabid=user.userid)
                list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city)
                list_of_testing_labs = TestingLab.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city)
                p = Doctor.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city).exclude(
                    clinic_name='')
                for i in p:
                    list_of_doctors[i] = i.clinic_fee
                location = d1.city + ',' + d1.state + ',' + d1.country
                request.session['country'] = d1.country.strip()
                request.session['city'] = d1.city.strip()
                request.session['state'] = d1.state.strip()

            elif (user.user_type == 'Hospital'):
                d1 = Hospital.objects.get(hospitalid=user.userid)
                list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city)
                list_of_testing_labs = TestingLab.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city)
                p = Doctor.objects.filter(verified="Yes").filter(country=d1.country).filter(city=d1.city).exclude(
                    clinic_name='')
                for i in p:
                    list_of_doctors[i] = i.clinic_fee
                location = d1.city + ',' + d1.state + ',' + d1.country
                request.session['country'] = d1.country.strip()
                request.session['city'] = d1.city.strip()
                request.session['state'] = d1.state.strip()
            else:
                country = "India"
                city = "Delhi"
                list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
                list_of_testing_labs = TestingLab.objects.filter(verified="Yes").filter(country=country).filter(
                    city=city)
                p = Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city).exclude(
                    clinic_name='')
                for i in p:
                    list_of_doctors[i] = i.clinic_fee
                location = city + ',NCT' + ',' + country
                request.session['country'] = country
                request.session['city'] = city
                request.session['state'] = "NCT"

        except:
            country="India"
            city="Delhi"
            list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            list_of_testing_labs = TestingLab.objects.filter(verified="Yes").filter(country=country).filter(
                city=city)
            p = Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city).exclude(
                clinic_name='')
            for i in p:
                list_of_doctors[i] = i.clinic_fee
            location =city + ',NCT'+ ',' + country
            request.session['country'] = country
            request.session['city'] = city
            request.session['state'] = "NCT"
    country=request.session['country']
    state=request.session['state']
    city=request.session['city']
    if city not in list_of_cities1(state):
        city="Select"
    if(state not in get_states(country)):
        state="Select"
    if(len(list_of_hospitals)==0 and len(list_of_testing_labs)==0 and len(list_of_doctors)==0):
        messages.info(request, "No Medical Facility Registered in This Area")
    return render(request,'main_app/Hospital_Selection.html',context={"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),"location":location,'list_of_countries':lis_of_countries,"list_of_hospitals":list_of_hospitals,"list_of_testing_labs":list_of_testing_labs,"list_of_doctors":list_of_doctors,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})


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
    #print(start_time)
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
    try:
        country=request.GET.get("country")
        lis_of_states=get_states(country)
        return JsonResponse(data=lis_of_states,safe=False)
    except:
        messages.info(request,"You Can not Access this Page")
        return redirect("/")

def list_of_city(request):
    try:
        state=request.GET.get("city")
        list_of_cities=list_of_cities1(state)
        return JsonResponse(data=list_of_cities, safe=False)
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")
def list_of_hospital(request):
     try:
        filter_type=request.GET.get("filter")

        filter=filter_type
        #print(filter)
        lis_of_countries = geo_plug.all_CountryNames()
        list_of_speciality=get_specialities()
        tests = getTests();
        list_of_tests = []
        for i in tests:
            list_of_tests.extend(i.testlist)
        p=[]
        city = request.session['city']
        state = request.session['state']
        country = request.session['country']
        location = city + ',' + state + ',' + country

        if(filter_type=='speciality'):
           speciality = request.GET['speciality']
           list_of_hospital=[]
           #filter="Hospitals"
           k1=HospitalSpeciality.objects.filter(speciality=speciality)
           list_of_doctors={}
           if(country==""):
               for i in k1:
                   list_of_hospital.append(Hospital.objects.get(hospitalid=i.hospitalid))
               list_of_clinics = Doctor.objects.filter(specialization=speciality)
           else:
               for i in k1:
                   p12=Hospital.objects.filter(hospitalid=i.hospitalid).filter(country=country).filter(city=city)
                   if(len(p12)>0):
                       list_of_hospital.append(p12[0])
               list_of_clinics=Doctor.objects.filter(specialization=speciality).filter(country=country).filter(city=city).exclude(clinic_name="")
           for i in list_of_clinics:
               list_of_doctors[i]=i.clinic_fee
           if(len(list_of_hospital)==0 and len(list_of_clinics)==0):
                messages.info(request,"No Doctor Registered for this Speciality")
           return render(request, "main_app/Hospital_Selection.html",
                          context={"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),"search_value":speciality,"filter":filter,"location":location,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality,"list_of_doctors": list_of_doctors,"list_of_hospitals":list_of_hospital,'list_of_countries':lis_of_countries,})
        elif(filter_type=='Test_Name'):
            testname=request.GET['Test_Name'];
            p=[]
            k=TestPricing.objects.filter(testname=testname)
            if(country==""):
                for i in k:
                    p.append(TestingLab.objects.get(tlabid=i.tlabid))
            else:
                for i in k:
                    p12=TestingLab.objects.filter(tlabid=i.tlabid).filter(country=country).filter(city=city)
                    if (len(p12)>0):
                        p.append(p12[0])
            #filter="Testing_Lab"
            list_of_tests = list_of_medical_tests();

            if (len(p) == 0):
                messages.info(request, "No Testing Lab Registered for this test")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),"list_of_testing_labs": p,"location":location,"filter":filter,"search_value":testname, "filter": filter,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality,'list_of_countries': lis_of_countries})

        elif(filter_type=='Hospitals'):
            #print(filter_type)
            if(country==""):
                p = Hospital.objects.filter(verified="Yes")
            else:
                p = Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            #filter="Hospitals"
            if (len(p) == 0):
                messages.info(request, "No Hospitals Registered in this location")
        elif(filter_type=="All"):
            list_of_doctors={}
            list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            list_of_testing_labs = TestingLab.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            p= Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city).exclude(
                clinic_name='')
            for i in p:
                list_of_doctors[i] = i.clinic_fee
            if (len(list_of_hospitals) == 0 and len(list_of_testing_labs) == 0 and len(list_of_doctors) == 0):
                messages.info(request,"No Medical Facility Registered In this Area")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location": location, "list_of_testing_labs": list_of_testing_labs,"list_of_doctors":list_of_doctors,"list_of_hospitals":list_of_hospitals, "filter": filter,
                                   'list_of_countries': lis_of_countries, "list_of_tests": list_of_tests,
                                   "list_of_speciality": list_of_speciality,"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state)})
        elif(filter_type=='Testing_Labs'):
            if(country==""):
                p = TestingLab.objects.filter(verified="Yes")
            else:
                p=TestingLab.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            #filter="Testing_Labs"
            #print(filter_type)
            if (len(p) == 0):
                messages.info(request, "No Testing Lab Registered in this Location")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_testing_labs": p, "filter": filter,
                                   "country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        elif(filter_type=='Clinics'):
            list_of_doctors={}
            if(country==""):
                p = Doctor.objects.filter(verified="Yes").exclude(clinic_name='')
            else:
                p=Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city).exclude(clinic_name='')
            for i in p:
                list_of_doctors[i]=i.clinic_fee
            #filter="Clinics"
            #print(filter_type)
            #print(p)
            if (len(p) == 0):
                messages.info(request, "No Clinic Registered in this Location")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_doctors": list_of_doctors,"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),"filter": filter,
                                   'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})

        elif (filter_type == 'Clinic_Name'):
            search_value = request.GET.get("search_values")
            if(country==""):
                p = Doctor.objects.filter(verified="Yes").filter(clinic_name__iexact=search_value)
            else:
                for i in Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city):
                    s1=search_value.casefold()
                    s2=i.clinic_name.casefold()
                    if(s2.find(s1)!=-1):
                        p.append(i)
            #print(p)
            if(len(p)==0):
                messages.info(request, "No Clinic Registered of this name")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_doctors": p,"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),"filter": filter,"search_value":search_value,
                                   'list_of_countries': lis_of_countries, "list_of_tests": list_of_tests,
                                   "list_of_speciality": list_of_speciality})

        elif(filter_type=='Location'):
            country=request.GET.get("country").strip()
            city=request.GET.get("city").strip()
            state=request.GET.get("state").strip()
            #print(City,State,Country)
            list_of_doctors={}
            request.session['city']=city
            request.session['state']=state
            request.session['country']=country
            location = city + ',' + state + ',' + country
            list_of_hospitals = Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            list_of_testing_labs = TestingLab.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            p = Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city).exclude(
                clinic_name='')
            for i in p:
                list_of_doctors[i] = i.clinic_fee
            if (len(list_of_hospitals) == 0 and len(list_of_testing_labs) == 0 and len(list_of_doctors) == 0):
                messages.info(request,"No Medical Facility Registered In this Area")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location": location, "list_of_testing_labs": list_of_testing_labs,
                                   "list_of_doctors": list_of_doctors, "list_of_hospitals": list_of_hospitals,
                                   "filter": filter,
                                   'list_of_countries': lis_of_countries, "list_of_tests": list_of_tests,
                                   "list_of_speciality": list_of_speciality, "country": country, "state": state,
                                   "city": city, "list_of_states": get_states(country),
                                   "list_of_cities": list_of_cities1(state)})

        elif (filter_type == 'Doctor_Name'):
            p = {}
            search_value = request.GET.get("search_values")

            if(country==""):
                k=Doctor.objects.filter(verified="Yes")
            else:
                k=Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city)
                print(k)
            for i in k:
                s1=search_value.casefold()
                s2=i.doctorid.name.casefold()
                if (s2.find(s1)!=-1):#i.doctorid.name.casefold() == search_value.casefold()):
                    if(i.clinic_name==''):
                        k1=HospitalSpeciality.objects.filter(hospitalid=i.hospitalid).filter(speciality=i.specialization)
                        #print("doctor",i.hospitalid)
                        try:
                            p[i]=k1[0].price
                            #print(k1[0].price)
                        except:
                            messages.info(request, "No Doctor of this name Registered")
                    else:
                       p[i]=i.clinic_fee
            #print(p,search_value)
            if(len(p)==0):
                messages.info(request, "No Doctor of this name Registered")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),"location":location,"list_of_doctors": p,"filter":filter,"search_value":search_value, 'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        elif(filter_type=='Hospital_Name'):
            p=[]
            search_value=request.GET.get("search_values")
            if(country==""):
                k=Hospital.objects.filter(verified="Yes")
            else:
                k=Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            for i in k:
                s1=i.hospitalid.name.casefold()
                s2=search_value.casefold()
                if(s1.find(s2)!=-1):
                    p.append(i)
                    break;
            #filter="Hospital"
            if(len(p)==0):
                messages.info(request,"No Hospital Registered with this Name")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_hospitals": p,"search_value":search_value, "filter": filter, 'list_of_countries': lis_of_countries,
                                   "list_of_tests": list_of_tests, "list_of_speciality": list_of_speciality,"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state)})
        elif(filter_type=='Testing_Lab'):
            search_value = request.GET.get("search_values")
            p=[]
            if(country==""):
                k=TestingLab.objects.filter(verified="Yes")
            else:
                k=TestingLab.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            for i in k:
                if(i.tlabid.name.casefold()==search_value.casefold()):
                    p.append(i);
            if(len(p)==0):
                messages.info(request,"No Testing lab registered with this name")

            return render(request, "main_app/Hospital_Selection.html",
                                  context={"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),"location":location,"list_of_testing_labs": p, "filter": filter,"search_value":search_value,
                                           'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        if(filter!=None):
            return render(request,"main_app/Hospital_Selection.html",context={"location":location,"list_of_hospitals":p,"filter":filter,"country":country,"state":state,"city":city,"list_of_states":get_states(country),"list_of_cities":list_of_cities1(state),'list_of_countries':lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        else:
            return redirect("/Hospital_Selection/")
     except:

        return redirect("/Hospital_Selection/")

def Selected_Service_Provider(request,user_id):
    try:
        user=UserDetails.objects.get(userid=user_id)
        request.session['user_type_Id']=int(user_id)
        #print(user.user_type)
        if(user.user_type=="Hospital"):
            p = Hospital.objects.get(hospitalid=user_id)
            k=HospitalSpeciality.objects.filter(hospitalid=p)
            k1=Hospital_News.objects.filter(hospitalid=p)
            Specialities=[]
            for i in k:
                Specialities.append(i.speciality)
            dict1={}
            poke = pd.read_csv("main_app/Specialities_Images.csv")
            list1 =poke['Speciality'].tolist()
            list2=poke['Speciality_Image'].tolist()
            #print(list1,list2)
            for i in Specialities:
                dict2={}
                if i in list1:
                    l0=HospitalSpeciality.objects.filter(speciality=i).filter(hospitalid=user_id)
                    dict2[list2[list1.index(i)]]=l0[0].price
                    dict1[i]=dict2
            return render(request,"main_app/Hospital_Testing_Lab_Profile.html",context={"Hospital_News":k1,"Hospital_Details":p,"specialities":dict1})
        elif(user.user_type=="Testing Lab"):
            p = TestingLab.objects.get(tlabid=user_id)
            k = TestPricing.objects.filter(tlabid=user_id)
            Tests = []
            for i in k:
                Tests.append(i)
            return render(request, "main_app/Hospital_Testing_Lab_Profile.html", context={"Testing_Lab_Details": p, "specialities": Tests})
        elif(user.user_type=="Patient"):
            p=Patient.objects.get(patientid=user.userid)
            return render(request,"main_app/User_Profile.html",context={"User_Details":p})
    except:
        return redirect("/accounts/signup/redirect/")
def Add_Prescription(request):
    Patient_Email=""
    Appointment_Id=""
    try:
        user=UserDetails.objects.get(email=request.session['email'])
        if(user.user_type=="Doctor"):
            try:
                Patient_Email=request.POST['Email']
                Appointment_Id=request.POST['id']
            except:
                pass
            return render(request,"main_app/Prescription.html",context={"Patient_Email":Patient_Email,'Appointment_Id':Appointment_Id})
        else:
            messages.info(request, "You Can not Access this Page")
            return redirect("/")
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")
def submit_Prescription(request):
    try:
        Appointment_Id=request.POST['Appointment_Id']
        prescription = request.FILES['prescription']
        b1=Appointments.objects.get(appointmentid=int(Appointment_Id))
        b1.Prescription=prescription
        b1.save()
        email=request.session['email']
        user1=UserDetails.objects.get(email=email)
        p="/dashboard/"+str(user1.userid)
        return redirect(p)
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")
    #return render(request,"main_app/Doctor_Testing_Lab_Dashboard.html",context={"list_of_Appointments":dict})
def Payment(request):
        try:    #print(request.GET['time_slot'])
            try:
                email = request.session['email']
                user1=UserDetails.objects.get(email=email)
                if(user1.user_type!="Patient"):
                    messages.info(request,"You are not allowed to book Appointment")
                    return redirect("/Hospital_Selection/")
            except:
                messages.info(request,"Please Login/Register")
                return redirect('/accounts/signin/')

            service_provider_id=request.GET['service_provider_id']
            request.session['user_type_Id']=service_provider_id
            user = UserDetails.objects.get(userid=service_provider_id)
            if(user.user_type=="Hospital" or user.user_type=="Doctor"):
                mode=request.session['mode']
                doctorid=service_provider_id#request.GET['doctorid']
                email=request.session['email']
                i=UserDetails.objects.get(email=email)
                patientname=i.name
                patientemail=i.email
                i=Doctor.objects.get(doctorid=int(doctorid))
                doctordetails=i
                speciality=i.specialization
                if(user.user_type=="Hospital"):
                    l1=HospitalSpeciality.objects.filter(hospitalid=i.hospitalid).filter(speciality=speciality)
                    amount_paid =l1[0].price
                else:
                    if(i.clinic_name==''):
                        l1 = HospitalSpeciality.objects.filter(hospitalid=i.hospitalid).filter(speciality=speciality)
                        amount_paid = l1[0].price
                    else:
                        amount_paid = i.clinic_fee
                appointment_date=request.session["date"]
                appointment_time=request.GET['time_slot']
                #print(appointment_time)
                request.session['time'] = appointment_time
                meeting_url=None
                if (mode == 'Online'):
                   appointment_time=request.GET['time_slot']
                   request.session['meeting_url']=create_zoom_meeting(appointment_date,appointment_time)
                   meeting_url=request.session['meeting_url']
                return render(request, "main_app/Confirm_Appointment.html",
                          context={"meeting_url":meeting_url,"mode": mode, "patientname": patientname, "patientemail": patientemail,
                                   "speciality": speciality, "amount_paid": amount_paid,"date":appointment_date,"time":appointment_time,"userdetails":doctordetails})
            elif(user.user_type=="Testing Lab"):
                mode = "Offline"
                p1 = UserDetails.objects.get(email=request.session['email'])
                patientname = p1.name
                patientemail = p1.email
                speciality = request.session['speciality1']
                l1 = TestPricing.objects.filter(tlabid=user.userid).filter(
                    testname=request.session['speciality1'])
                amount_paid = l1[0].price
                TestingLabId = TestingLab.objects.get(tlabid=user.userid)
                t = Appointment_Timings.objects.filter(service_provider_id=user).filter(date=request.session['date'])
                appointment_time = request.GET['time_slot']
                request.session['time'] = appointment_time
                appointment_date=request.session['date']
                return render(request, "main_app/Confirm_Appointment.html",
                              context={"mode": mode, "patientname": patientname, "patientemail": patientemail,
                                       "speciality": speciality, "amount_paid": amount_paid, "date": appointment_date,
                                       "time": appointment_time, "userdetails": TestingLabId})
        except:
            messages.info(request, "You Can not Access this Page")
            return redirect("/")
def cancel_appointment(request):
    messages.info(request,"Appointment Canceled Sucessfully")
    return redirect('/Hospital_Selection')

def change_date(request):
    try:
        request.session['date']=request.POST['date']
        service_provider = UserDetails.objects.get(userid=request.POST['service_provider_id'])
        if(service_provider.user_type=="Testing Lab"):
            User_Profile = TestingLab.objects.get(tlabid=request.POST['service_provider_id'])
        else:
            User_Profile=Doctor.objects.get(doctorid=request.POST['service_provider_id'])
        slots=available_slots(service_provider,request.session['date'])
        return render(request, "main_app/Book_Time_Slot.html",
                          context={"date": request.session['date'], "User_Profile": User_Profile, 'slots': slots})
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")
def available_slots(service_provider,date1):
    slots = []
    t = Appointment_Timings.objects.filter(service_provider_id=service_provider).filter(date=date1)
    if len(t) > 0:
        if (t[0].available == False):
            slots=[]
        else:
            for i in t:
                if (i.Booked == False):
                    t12 = i.time.split(":")
                    d12 = str(i.date).split("-")
                    #print(d12)
                    da = datetime.datetime(int(d12[0]), int(d12[1]), int(d12[2]), int(t12[0]), int(t12[1]), int(t12[2]))
                    slots.append(da)

    else:
        p13=UserDetails.objects.get(userid=service_provider.userid)
        if(p13.user_type=="Doctor"):
            d1=Doctor.objects.get(doctorid=service_provider)
            start_time=d1.start_time.split(":")
            end_time=d1.end_time.split(":")
            #print(start_time,end_time)
        else:
            t1 = TestingLab.objects.get(tlabid=service_provider)
            start_time = t1.start_time.split(":")
            end_time = t1.end_time.split(":")
            print(start_time, end_time)
            #start_time=[9,0,0]
            #end_time=[16,0,0]
        date = date1.split("-")
        x = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(start_time[0]), int(start_time[1]), 0)
        y = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(end_time[0]), int(end_time[1]), 0)
        while (x < y):
            b12 = Appointment_Timings()
            b12.service_provider_id = service_provider
            b12.date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
            b12.time = x.strftime("%X")
            t12 = b12.time.split(":")
            d12 = str(b12.date).split("-")
            da = datetime.datetime(int(d12[0]), int(d12[1]), int(d12[2]), int(t12[0]), int(t12[1]), int(t12[2]))
            slots.append(da)
            b12.save()
            x += datetime.timedelta(minutes=30)
    return slots
def Appointment_Details_Submission(request):
       try:
            try:
                data=request.POST['data']
            except:
                k=Appointments.objects.all().order_by('-appointmentid')
                p="/Appointment_Details/"+str(k[0].appointmentid)
                return redirect(p);
            user = UserDetails.objects.get(userid=int(request.session['user_type_Id']))
            doctor_details=""
            if(user.user_type=="Hospital" or user.user_type=="Doctor"):
                a1=Appointments()
                mode=request.session['mode']
                doctorid=int(request.session['user_type_Id'])
                email=request.session['email']
                i=UserDetails.objects.get(email=email)
                a1.patientname=i.name
                a1.patientemail=i.email
                i=Doctor.objects.get(doctorid=int(doctorid))
                a1.doctoremail=i.doctorid.email
                doctor_details=i
                hospital_id=i.hospitalid
                speciality=i.specialization
                a1.Speciality=speciality
                if(user.user_type=="Hospital"):
                    l1=HospitalSpeciality.objects.filter(hospitalid=hospital_id).filter(speciality=speciality)
                    a1.amount_paid =l1[0].price
                else:
                    if (i.clinic_name == ''):
                        l1 = HospitalSpeciality.objects.filter(hospitalid=i.hospitalid).filter(speciality=speciality)
                        a1.amount_paid = l1[0].price
                    else:
                        a1.amount_paid = i.clinic_fee
                a1.appointment_date=request.session["date"]
                d=a1.appointment_date
                a1.appointment_time=request.session['time']
                if (mode == 'Online'):

                   a1.meeting_url=request.session['meeting_url']
                   a1.mode_of_meeting = mode
                else:
                    a1.mode_of_meeting = mode
                b1=Appointment_Timings.objects.filter(service_provider_id=user).filter(date=a1.appointment_date).filter(time=a1.appointment_time)
                #print(b1)
                b1.update(Booked=True)
                a1.save()
            elif(user.user_type=="Testing Lab"):
                a1 = Appointments()
                mode = "Offline"
                TestingLabId = request.session['user_type_Id']
                p1 = UserDetails.objects.get(email=request.session['email'])
                a1.patientname = p1.name
                a1.patientemail = p1.email
                a1.Speciality = request.session['speciality1']
                l1 = TestPricing.objects.filter(tlabid=user.userid).filter(
                    testname=request.session['speciality1'])
                a1.amount_paid = l1[0].price
                a1.TestingLabId = TestingLab.objects.get(tlabid=user.userid)
                t = Appointment_Timings.objects.filter(service_provider_id=user).filter(date=request.session['date'])
                a1.mode_of_meeting = "Offline"
                a1.appointment_time = request.session['time']
                a1.appointment_date=request.session['date']

                b1 = Appointment_Timings.objects.filter(service_provider_id=user).filter(date=a1.appointment_date).filter(time=a1.appointment_time)
                #print(len(b1))
                b1.update(Booked=True)
                a1.save()

            return render(request,"main_app/Receipt.html",context={"Appointment_Details":a1,"service_provider":user,"doctor_details":doctor_details})
       except:
            messages.info(request, "You Can not Access this Page")
            return redirect("/")

def select_speciality(request,service_provider_id):
    try:
        user = UserDetails.objects.get(userid=service_provider_id)
        try:
            date=request.session['date']
        except:
            date=''
        if(user.user_type=="Hospital"):
            p = Hospital.objects.get(hospitalid=service_provider_id)
            k = HospitalSpeciality.objects.filter(hospitalid=p)
            Specialities = []
            for i in k:
                Specialities.append(i.speciality)
            return render(request,"main_app/Select_Speciality.html",context={"date":date,"specialities":Specialities,"Hospital_Details":p})
        elif(user.user_type=="Testing Lab"):
            p = TestingLab.objects.get(tlabid=service_provider_id)
            k = TestPricing.objects.filter(tlabid=service_provider_id)
            Tests = []
            for i in k:
                Tests.append(i.testname)
            return render(request, "main_app/Select_Speciality.html", context={"date":date,"Testing_Lab_Details": p, "specialities": Tests})
        else:
            messages.info(request, "Invalid Service Provider Id")
            return redirect("/")

    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")
def book_appointment1(request,speciality,service_provider_id):
    try:
        user=UserDetails.objects.get(userid=service_provider_id)
        request.session['speciality'] = speciality
        if(user.user_type=="Hospital"):
            p=Doctor.objects.filter(specialization=speciality).filter(hospitalid=service_provider_id).filter(verified="Yes")
            list_of_doctors=[]
            for i in p:
                #user1=User.objects.get()
                t=Appointment_Timings.objects.filter(service_provider_id=i.doctorid).filter(date=request.session['date'])
                #print(len(t))
                if len(t)==0:
                    list_of_doctors.append(i)
                else:
                    #print(t[0].Slots_Booked)
                    #print("availabel",t[0].available)
                    if(t[0].available==True):
                        list_of_doctors.append(i)
                        #list_of_doctors[i] = time_slots.split(",")
            k = Hospital.objects.get(hospitalid=user.userid)
            print("list",list_of_doctors)
            return render(request, "main_app/Select_Doctor.html", context={"list_of_Doctors": list_of_doctors,"Hospital_Details":k})
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")

def Appointment_Details_Submission1(request):
    try:
        try:
            request.session["date"] = request.GET['date']
            #request.session['user_type_Id']=int(request.GET['doctorid'])
        except:
            pass
        service_provider_id=int(request.GET['service_provider_id'])
        #user=UserDetails.objects.get(userid=request.session['user_type_Id'])
        user = UserDetails.objects.get(userid=service_provider_id)
        if(user.user_type=='Doctor' or user.user_type=="Hospital"):
                request.session['mode'] = request.GET['mode']
                #request.session['doctorid'] = request.GET['doctorid']
                #print(request.GET['doctorid'])
                service_provider = UserDetails.objects.get(userid=user.userid)#int(request.GET['doctorid']))
                User_Profile=Doctor.objects.get(doctorid=user.userid)#int(request.GET['doctorid']))

        elif(user.user_type=='Testing Lab'):
                request.session['mode']="Remote"
                request.session['doctorid']=request.session['user_type_Id']
                service_provider = UserDetails.objects.get(userid=service_provider_id)#request.session['doctorid'])
                User_Profile = TestingLab.objects.get(tlabid=service_provider_id)
                request.session['speciality1']=request.GET['speciality']
        list_of_speciality = get_specialities()
        list_of_tests = list_of_medical_tests()
        list_of_doctors=[]
        slots = available_slots(service_provider,request.session['date'])
        list_of_doctors.append(User_Profile)
        location = request.session['city'] + ',' + request.session['state'] + ',' + request.session['country']
        if(len(slots)==0):
                messages.info(request, "Doctor not availaible on this date")
                if(user.user_type=="Doctor"):
                    return render(request, "main_app/Hospital_Selection.html",
                                  context={"list_of_doctors": list_of_doctors, "filter": "Doctor_Name", "search_value":User_Profile.doctorid.name ,
                                           'list_of_countries': geo_plug.all_CountryNames(), "list_of_tests": list_of_tests,
                                           "list_of_speciality": list_of_speciality})
                else:
                    return redirect('/Hospital_Selection')

        return render(request, "main_app/Book_Time_Slot.html", context={"date":request.session['date'],"User_Profile": User_Profile, 'slots': slots})

    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")
def chosen_date(request):
    try:
        if (request.GET.get("date") != None):
            request.session['date']=request.GET.get("date")
            return JsonResponse(request.session['date'],safe=False)
        else:
            messages.info(request, "You Can not Access this Page")
            return redirect("/")

    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")

def user_location(request):
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        longitude=request.GET["longitude"]
        latitude=request.GET["latitude"]
        location=geolocator.reverse(str(latitude)+","+str(longitude))
        address=location.raw['address']
        request.session['country']=address['country'].strip()
        request.session['state']=address['state'].strip()
        lis=list_of_cities1(request.session['state'])
        if address['county'] in lis:
                request.session['city']=address['county'].strip()
        else:
            request.session['city'] = address['state_district'].strip()
        return JsonResponse(request.GET['longitude'], safe=False)
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")
    #print(request.session['city'])
    #print(address)


def search_appointments(request):
    try:
        no_of_Appointments_completed = 0;
        no_of_Appointments = 0;
        dt=datetime.datetime.now();
        email = request.session['email']
        filter_type=request.GET['filter']
        search_values=request.GET['search_values']
        dict = {}
        user=UserDetails.objects.get(email=email)
        if (user.user_type == 'Patient'):
            User_Profile=Patient.objects.get(patientid=user.userid)
            if(filter_type=='Date'):
                list_of_Appointments = Appointments.objects.filter(patientemail=email).filter(appointment_date=search_values)
                #print(list_of_Appointments)
                dict=appoin(list_of_Appointments)
            else:
                lis_of_doctors=UserDetails.objects.filter(user_type="Doctor").filter(name__contains=search_values)
                for i in lis_of_doctors:
                    list_of_Appointments=Appointments.objects.filter(patientemail=email).filter(doctoremail__iexact=i.email)
                    for j in list_of_Appointments:
                        if (j.Prescription != ""):
                            dict[j] = j
                        else:
                            dict[j] = "Upload Prescription"

            return render(request, 'main_app/Doctor_Testing_Lab_Dashboard.html',
                          context={"list_of_Appointments": dict, "User_Details": User_Profile,"filter_type":filter_type,"search_value":search_values})

        elif (user.user_type == 'Doctor'):
                i=Doctor.objects.get(doctorid=user)
                User_Profile = i
                available=True
                l1 = Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=datetime.date.today())
                if (len(l1) > 0):
                    available = l1[0].available
                online_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                    appointment_date__month=dt.month).filter(mode_of_meeting="Online").count()
                no_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                    appointment_date__month=dt.month).count();
                no_of_Appointments_completed == Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                    appointment_date__month=dt.month).exclude(Prescription='').count();
                if (filter_type == 'Date'):
                        list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter( appointment_date=search_values)
                else:
                        list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                            patientname__contains=search_values)
                return render(request, 'main_app/Doctor_Testing_Lab_Dashboard.html',
                              context={"available": available, "list_of_Appointments": appoin(list_of_Appointments),
                                       "User_Details": User_Profile,
                                       "no_of_Appointments_completed": no_of_Appointments_completed,
                                       "no_of_Appointments": no_of_Appointments,
                                       "online_Appointments": online_Appointments,"filter_type":filter_type,"search_value":search_values})

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
            available=True
            l1 = Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=datetime.date.today())
            if (len(l1) >0):
                available = l1[0].available
            no_of_Appointments_completed = Appointments.objects.filter(TestingLabId=User_Profile).filter(
                appointment_date__month=dt.month).exclude(Prescription='').count();
            no_of_Appointments = Appointments.objects.filter(TestingLabId=User_Profile).filter(
                appointment_date__month=dt.month).count();
            tests = []
            list_of_tests = TestPricing.objects.filter(tlabid=User_Profile)
            for i in list_of_tests:
                t1 = Appointments.objects.filter(TestingLabId=User_Profile).filter(
                    appointment_date__month=dt.month).filter(Speciality=i.testname).count();
                no_of_test_appointments.append(t1)
                tests.append(i.testname)
            return render(request, 'main_app/Doctor_Testing_Lab_Dashboard.html',
                          context={"available": available, "dict_test": no_of_test_appointments,
                                   "Test_Names": json.dumps(tests),
                                   "list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile,
                                   "no_of_Appointments_completed": no_of_Appointments_completed,
                                   "no_of_Appointments": no_of_Appointments,"filter_type":filter_type,"search_value":search_values})
            # print(p)

    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")

def Appointment_Details(request,appointment_id):
    try:
        doctor_details=""
        Appointment_Details1=Appointments.objects.get(appointmentid=appointment_id)
        if(Appointment_Details1.doctoremail):
            user=UserDetails.objects.get(email=Appointment_Details1.doctoremail)

            doctor_details=Doctor.objects.get(doctorid=user.userid)
        return render(request,'main_app/Receipt.html',context={'doctor_details':doctor_details,'Appointment_Details':Appointment_Details1})
    except:
        messages.info(request,"No Appointment Available");
        return redirect("/")
def admin_search_appointments(request):
    try:
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
                l12 = Appointment_Timings.objects.filter(service_provider_id=i.doctorid.userid).filter(date=dt)
                if (len(l12) > 0):
                    #print(len(l12))
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
                    l12 = Appointment_Timings.objects.filter(service_provider_id=i.doctorid.userid).filter(date=dt)
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

        #print(list_of_speciality)
        filter_type = request.GET['filter']
        Appointments1 = []
        if (filter_type == "speciality"):

            search_values = request.GET['search_values1']
        else:
            search_values = request.GET['search_values']

        #print(search_values)
        for i in list_of_doctors:
                #print(i.doctorid.email)
                if (filter_type == "Date"):
                        p1=Appointments.objects.filter(appointment_date=search_values).filter(doctoremail=i.doctorid.email)
                        for j in p1:
                            Appointments1.append(j)
                elif (filter_type == "Doctor_Name"):
                    doctor = UserDetails.objects.filter(name__contains=search_values).filter(user_type="Doctor")
                    for j in doctor:
                        Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(doctoremail=j.email)
                    break;
                elif(filter_type=="Patient_Name"):
                    Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(patientname__contains=search_values)
                    break;
                elif(filter_type=="speciality"):
                    Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(
                        Speciality=search_values)
                    break;
        #print(Appointments1)
        return render(request, "main_app/Hospital_Dashboard.html",
                      context={"filter_type":filter_type,"search_value":search_values,"speciality":speciality,"list_of_Appointments": Appointments1, "doctors_data": doctors_data,
                               "list_of_speciality": json.dumps(list(list_of_speciality.keys())),"hospitalid":user.userid,
                               "list_of_speciality_appointments": list(list_of_speciality.values()),
                               "Online_consultations_today": Online_consultations_today,
                               "appointments_this_month": appointments_this_month, "earning_this_month": earning_this_month,
                               "appointments_today": appointments_today,"filter_type":filter_type,"search_value":search_values})
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")


def availablity(request):
    try:
        user = UserDetails.objects.get(email=request.session['email'])
        s=request.POST['start'].split('T')
        e=request.POST['end'].split('T')
        start=s[0].split('-')
        end=e[0].split('-')
        starttime=s[1].split(':')
        endtime=e[1].split(':')
        start1=datetime.datetime(int(start[0]),int(start[1]),int(start[2]),int(starttime[0]),int(starttime[1]),0)
        end1=datetime.datetime(int(end[0]),int(end[1]),int(end[2]),int(endtime[0]),int(endtime[1]),0)
        date=start1
        list_of_appointments = []
        #print(start,end)
        if (user.user_type == "Doctor"):
            d1 = Doctor.objects.get(doctorid=user.userid)
            start_time = d1.start_time.split(":")
            end_time = d1.end_time.split(":")
            #print(start_time, end_time)
        else:
            t1 = TestingLab.objects.get(tlabid=user.userid)
            start_time = t1.start_time.split(":")
            end_time = t1.end_time.split(":")
            #print(start_time, end_time)
        user_start_time = datetime.datetime(int(start[0]), int(start[1]), int(start[2]), int(start_time[0]), int(start_time[1]), 0)
        user_end_time=datetime.datetime(int(start[0]), int(start[1]), int(start[2]), int(end_time[0]), int(end_time[1]), 0)
        while(user_start_time<=end1):
            if(user.user_type=="Testing Lab"):
                tester=TestingLab.objects.get(tlabid=user.userid)
                service_provider=UserDetails.objects.get(userid=user.userid)
                #print(Appointment_Timings.objects.filter(service_provider_id=service_provider).filter(
                    #date=user_start_time.date()).delete())
                if(user_start_time >= start1 and user_end_time <= end1):
                    b12 = Appointment_Timings()
                    b12.service_provider_id = service_provider
                    b12.date = user_start_time.date()
                    l2 = Appointments.objects.filter(appointment_date=user_start_time.date()).filter(
                        TestingLabId=tester)
                    for i in l2:
                        list_of_appointments.append(i)
                    b12.available=False
                    b12.save()
                    user_end_time += datetime.timedelta(days=1)
                    user_start_time += datetime.timedelta(days=1)
                else:
                    while (user_start_time < user_end_time):
                        b12 = Appointment_Timings()
                        b12.service_provider_id = service_provider
                        b12.date = user_start_time.date()
                        b12.time = user_start_time.strftime("%X")
                        if(user_start_time > start1 and user_start_time < end1):
                            l2 = Appointments.objects.filter(appointment_date=user_start_time.date()).filter(
                                TestingLabId=tester).filter(appointment_time=b12.time)
                            if(len(l2)>0):
                                list_of_appointments.append(l2[0])
                            b12.Booked=True
                        b12.save()
                        user_start_time += datetime.timedelta(minutes=30)
                        user_end_time += datetime.timedelta(days=1)
                        user_start_time += datetime.timedelta(hours=17)
            elif(user.user_type == "Doctor"):
                doctor = Doctor.objects.get(doctorid=user.userid)
                service_provider = UserDetails.objects.get(userid=user.userid)
                #print(Appointment_Timings.objects.filter(service_provider_id=service_provider).filter(date=user_start_time.date()).delete())
                #print()
                if (user_start_time >= start1 and user_end_time <= end1):
                    b12 = Appointment_Timings()
                    b12.service_provider_id = service_provider
                    b12.date = user_start_time.date()
                    b12.available = False
                    l2 = Appointments.objects.filter(appointment_date=user_start_time.date()).filter(
                        doctoremail=doctor.doctorid.email)
                    for i in l2:
                        list_of_appointments.append(i)
                    b12.save()
                    user_end_time += datetime.timedelta(days=1)
                    user_start_time += datetime.timedelta(days=1)
                else:
                    while (user_start_time < user_end_time):
                            b12 = Appointment_Timings()
                            b12.service_provider_id = service_provider
                            b12.date = user_start_time.date()
                            b12.time = user_start_time.strftime("%X")
                            if (user_start_time > start1  and user_start_time < end1):

                                l2 = Appointments.objects.filter(appointment_date=user_start_time.date()).filter(
                                    doctoremail=doctor.doctorid.email).filter(appointment_time=b12.time)

                                try:
                                    list_of_appointments.append(l2[0])
                                except:
                                    pass
                                b12.Booked = True
                            b12.save()
                            user_start_time += datetime.timedelta(minutes=30)

                    user_end_time += datetime.timedelta(days=1)
                    user_start_time += datetime.timedelta(hours=17)
            #date += datetime.timedelta(days=1)
            cancel_appointments(list_of_appointments,user)
        messages.info(request,"All Your Appointment between "+str(start1)+" and "+str(end1)+" are cancelled")
        str1="/dashboard/"+str(user.userid)
        return redirect(str1)
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")

def cancel_appointments(list_of_appointments,user):
    for i in list_of_appointments:
            i.delete();
            template = render_to_string('main_app/email_template.html',
            {
            'name': i.patientname,
            'user_type_name': user.user_type,
            'appointment_date':str(i.appointment_date.year)+'-'+str(i.appointment_date.month)+'-'+str(i.appointment_date.day),
            'fee': i.amount_paid,
             'domain': domain.getDomainName(),
            })
            email = EmailMessage(
                'Update relating to Appointment',
                template,
                settings.EMAIL_HOST_USER,
                [i.patientemail],
            )
            email.fail_silently = False
            email.send()

def report(request):
    try:
        start=request.POST['start']
        end=request.POST['end']
        user = UserDetails.objects.get(email=request.session['email'])
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
            user = UserDetails.objects.get(userid=i.doctorid.userid)
            # print(Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count())
            l2 = Appointments.objects.filter(appointment_date__range=[start,end]).filter(doctoremail=i.doctorid.email).count()
            list_of_speciality[i.specialization] += l2
            p1 = HospitalSpeciality.objects.filter(speciality=i.specialization).filter(hospitalid=user.userid)
            if (len(p1) == 0):
                l1.append(0)
                l1.append(0)
            else:
                for k1 in p1:
                    l1.append(l2)
                    l1.append(k1.price * l2)
            doctors_data[i] = l1
            appointments_this_month += l2
            appointments_today += Appointments.objects.filter(appointment_date__range=[start,end]).filter(
                doctoremail=i.doctorid.email).count()
            Online_consultations_today += Appointments.objects.filter(appointment_date__range=[start,end]).filter(
                mode_of_meeting="Online").filter(doctoremail=i.doctorid.email).count()
            k = Appointments.objects.filter(appointment_date__range=[start,end]).filter(
                doctoremail=i.doctorid.email).aggregate(Sum('amount_paid'))
            if (k['amount_paid__sum'] != None):
                earning_this_month += k['amount_paid__sum']
            l23 = Appointments.objects.filter(appointment_date__range=[start,end]).filter(doctoremail=i.doctorid.email)
            for i in l23:
                Appointments1.append(i)
        p=list(list_of_speciality.values())
        min1=min(p)
        max1=max(p)
        #print(list_of_speciality)
        data={"speciality": speciality, "list_of_Appointments": Appointments1,
        "doctors_data": doctors_data,
        "max":max1,"min":min1,
        "start":start,"end":end,
        "list_of_speciality": json.dumps(list(list_of_speciality.keys())),
        "list_of_speciality_appointments": list(list_of_speciality.values()),
        "Online_consultations_today": Online_consultations_today,
        "appointments_this_month": appointments_this_month, "earning_this_month": earning_this_month,
        "appointments_today": appointments_today}
        print(data)
        return render(request, "main_app/Report_Hospital.html", context=data)
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")

def add_news(request,id):
    user=UserDetails.objects.get(userid=id)
    if(user.user_type=="Hospital"):
        return render(request,"main_app/News.html",context={"id":id})
    else:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")

def submit_news(request):
    try:
        a1=Hospital_News()
        a1.Title=request.POST['title']
        a1.photos=request.FILES['file1']
        a1.Information=request.POST['About']
        a1.hospitalid=Hospital.objects.get(hospitalid=request.POST['id'])
        a1.save()
        str="dashboard/"+request.POST['id']
        return redirect(str)
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")
def edit_time(request,id):
    try:
        user=UserDetails.objects.get(userid=id)
        if(user.user_type=="Doctor"):
            d1=Doctor.objects.get(doctorid=id)
            d1.start_time=request.POST['start_time']
            d1.end_time=request.POST['end_time']
            d1.save()
        elif(user.user_type=="Testing Lab"):
            t1=TestingLab.objects.get(tlabid=id)
            t1.start_time=request.POST['start_time']
            t1.end_time=request.POST['end_time']
            t1.save()
        str1='/dashboard/'+str(id)
        return redirect(str1);
    except:
        messages.info(request, "You Can not Access this Page")
        return redirect("/")

def rate(request):
    aid=request.POST['aid']
    rating=request.POST['rating']
    email=request.session['email']
    user=UserDetails.objects.get(email=email)
    a1=Appointments.objects.get(appointmentid=aid)
    if(a1.doctoremail==None):
        p=a1.TestingLabId.tlabid;
        k=Ratings.objects.filter(influencerid=p).filter(raterid=user.userid).count();
        if(k==0):
            r=Ratings();
            r.influencerid=p;
            r.raterid=user;
            r.rating=rating;
            r.save()
        else:
            r=Ratings.objects.filter(raterid=user.userid).filter(influencerid=p)
            r.update(rating=rating);
        doctor1 = TestingLab.objects.get(tlabid=p)
        rat = Ratings.objects.filter(influencerid=doctor1.tlabid).aggregate(Avg('rating'))
        no_of_raters1 = Ratings.objects.filter(influencerid=doctor1.tlabid).count();
        # total_rat=doctor1.rating*doctor1.no_of_raters+int(rating)
        # rat=total_rat/(doctor1.no_of_raters+1)
        doctor1.rating = round(rat['rating__avg'],1);
        doctor1.no_of_raters = no_of_raters1
        doctor1.save();
    else:
        doctor =UserDetails.objects.get(email=a1.doctoremail)
        k = Ratings.objects.filter(influencerid=doctor.userid).filter(raterid=user.userid).count();
        if (k == 0):
            r = Ratings();
            r.influencerid = doctor;
            r.raterid = user;
            r.rating = rating;
            r.save()
        else:
            r = Ratings.objects.filter(raterid=user.userid).filter(influencerid=doctor.userid)
            r.update(rating = rating);
        doctor1=Doctor.objects.get(doctorid=doctor.userid)
        rat=Ratings.objects.filter(influencerid=doctor.userid).aggregate(Avg('rating'))
        no_of_raters1=Ratings.objects.filter(influencerid=doctor.userid).count();
        #total_rat=doctor1.rating*doctor1.no_of_raters+int(rating)
        #rat=total_rat/(doctor1.no_of_raters+1)
        doctor1.rating=round(rat['rating__avg'],1);
        doctor1.no_of_raters=no_of_raters1
        doctor1.save();
        if(True):
            hid=doctor1.hospitalid;
            no_of_doctors=Doctor.objects.filter(hospitalid=hid).count();
            ratings=Doctor.objects.filter(hospitalid=hid).aggregate(Sum('no_of_raters'));
            h=Hospital.objects.get(hospitalid=hid)
            total_rat=Doctor.objects.filter(hospitalid=hid).aggregate(Sum('rating'))['rating__sum'];
            h.rating=round(total_rat/no_of_doctors,1)
            h.no_of_raters=ratings['no_of_raters__sum']
            print(h.rating,total_rat,no_of_doctors)
            h.save()
        else:
            pass
    a1.rating=True;
    a1.rating_value=rating;
    a1.save();
    k="/dashboard/"+str(user.userid);
    messages.info(request,"Rating Added Successfully")
    return redirect(k)