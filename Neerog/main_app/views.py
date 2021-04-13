import time
from django.core.mail import send_mail, EmailMessage
from django.db.models import Sum
from django.template.loader import render_to_string
from main_app.models import*;
from main_app.medical_tests import *;
from .location import *;
from django.contrib import messages
import requests
from geopy.geocoders import Nominatim
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
from .medical_speciality import get_specialities
from .medical_tests import list_of_medical_tests
from .models import TestingLab

replace_dictionary={"u0101":"a","u012b":"i","u016b":"u","u0100":"A","u016a":"u"}

# Verification of the user certificate
"""def verify(request):
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
"""
def verify_certificate(request,id):
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
        p['Hospital'] = Hospital.objects.filter(verified="No")
        p['Doctor'] = Doctor.objects.filter(verified="No")
        p['Testing_Lab'] = TestingLab.objects.filter(verified="No")
        return render(request, "main_app/Verify_Certificate.html", context={'list_of_certificates': p})
    else:
        messages.info(request, "You Can't Access This Page!")
        return redirect("/")

def appoin(list_of_Appointments):
    dict={}
    no_of_appointment_completed=0
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
            user = UserDetails.objects.get(userid=i.doctorid.userid)
            # print(Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count())
            l2 = Appointments.objects.filter(appointment_date__month=dt.month).filter(
                doctoremail=i.doctorid.email).count()
            list_of_speciality[i.specialization] += l2
            p1 = HospitalSpeciality.objects.filter(speciality=i.specialization).filter(hospitalid=user.userid)
            if (len(p1) == 0):
                l1.append(0)
                l12 = Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=dt)
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
                    l12 = Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=dt)

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
                               "doctors_data": doctors_data,"hospitalid":user.userid,
                               "list_of_speciality": json.dumps(list(list_of_speciality.keys())),
                               "list_of_speciality_appointments": list(list_of_speciality.values()),
                               "Online_consultations_today": Online_consultations_today,
                               "appointments_this_month": appointments_this_month,
                               "earning_this_month": earning_this_month,"filter_type":"Date","appointments_today": appointments_today})
    if(user.user_type=='Patient'):
        i=Patient.objects.get(patientid=user)
        User_Profile=i;
        list_of_Appointments = Appointments.objects.filter(patientemail=email).order_by('-appointment_date')
        return render(request, 'main_app/Profile.html',
                              context={"filter_type":"Date","list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile})

    elif (user.user_type == 'Doctor'):
        User_Profile=Doctor.objects.get(doctorid=user.userid)
        l1=Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=datetime.date.today())
        available=True
        if(len(l1)>0):
            available=l1[0].available
        list_of_Appointments =Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).order_by('-appointment_date')
        online_Appointments=Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).filter(mode_of_meeting="Online").count()
        no_of_Appointments=Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).count();
        no_of_Appointments_completed=Appointments.objects.filter(doctoremail=User_Profile.doctorid.email).filter(appointment_date__month=dt.month).exclude(Prescription='').count();
        return render(request, 'main_app/Profile.html',
                      context={"available":available,"list_of_Appointments":appoin(list_of_Appointments) , "User_Details": User_Profile,
                               "no_of_Appointments_completed":no_of_Appointments_completed,
                               "no_of_Appointments": no_of_Appointments,
                               "online_Appointments": online_Appointments,"filter_type":"Date"})

    elif(user.user_type=="Testing Lab"):
        User_Profile=TestingLab.objects.get(tlabid=user.userid)
        list_of_Appointments = Appointments.objects.filter(TestingLabId=User_Profile).order_by('-appointment_date')
        no_of_test_appointments=[]
        available=True
        l1=Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=datetime.date.today())
        if(len(l1)>0):
            available=l1[0].available
        no_of_Appointments_completed=Appointments.objects.filter(TestingLabId=User_Profile).filter(appointment_date__month=dt.month).exclude(Prescription='').count();
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
                               "no_of_Appointments": no_of_Appointments,"filter_type":"Date"})
    elif (user.user_type == 'Moderator'):
        p = dict()
        p['Hospital'] = Hospital.objects.filter(verified="No")
        p['Doctor'] = Doctor.objects.filter(verified="No")
        p['Testing_Lab'] = TestingLab.objects.filter(verified="No")
        return render(request, "main_app/Verify_Certificate.html", context={'list_of_certificates': p})



def index(request):
    return render(request,'main_app/index.html')
def home(request):
    return render(request,'main_app/home.html')

def Hospitals(request):
    lis_of_countries = geo_plug.all_CountryNames()
    list_of_tests=list_of_medical_tests();
    list_of_speciality=get_specialities()
    city=request.session['city'].strip()
    state=request.session['state'].strip()
    country=request.session['country'].strip()
    location=city+','+state+','+country
    p = Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
    return render(request,'main_app/Hospital_Selection.html',context={"location":location,'list_of_countries':lis_of_countries,"list_of_hospitals":p,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})


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
    country=request.GET.get("country")
    lis_of_states=get_states(country)
    return JsonResponse(data=lis_of_states,safe=False)

def list_of_city(request):
    state=request.GET.get("city")
    list_of_cities=list_of_cities1(state)
    return JsonResponse(data=list_of_cities, safe=False)
def list_of_hospital(request):
     #try:
        filter_type=request.GET.get("filter")
        filter=filter_type
        print(filter)
        lis_of_countries = geo_plug.all_CountryNames()
        list_of_speciality=get_specialities()
        list_of_tests=list_of_medical_tests()
        p=[]
        try:
            city = request.session['city']
            state = request.session['state']
            country = request.session['country']
            location = city + ',' + state + ',' + country
        except:
            city=""
            state=""
            country=""
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
                messages.info(request,"No Doctor Available for this Speciality")
           return render(request, "main_app/Hospital_Selection.html",
                          context={"search_value":speciality,"filter":filter,"location":location,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality,"list_of_doctors": list_of_doctors,"list_of_hospitals":list_of_hospital,'list_of_countries':lis_of_countries,})
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
                messages.info(request, "No Testing Lab Available for this test")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"list_of_testing_labs": p,"location":location,"filter":filter,"search_value":testname, "filter": filter,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality,'list_of_countries': lis_of_countries})

        elif(filter_type=='Hospitals'):
            print(filter_type)
            if(country==""):
                p = Hospital.objects.filter(verified="Yes")
            else:
                p = Hospital.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            #filter="Hospitals"
            if (len(p) == 0):
                messages.info(request, "No Hospitals available")
        elif(filter_type=='Testing_Labs'):
            if(country==""):
                p = TestingLab.objects.filter(verified="Yes")
            else:
                p=TestingLab.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            #filter="Testing_Labs"
            print(filter_type)
            if (len(p) == 0):
                messages.info(request, "No Testing Lab Available")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_testing_labs": p, "filter": filter,
                                   'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        elif(filter_type=='Clinics'):
            list_of_doctors={}
            if(country==""):
                p = Doctor.objects.filter(verified="Yes").exclude(clinic_name='')
            else:
                p=Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city).exclude(clinic_name='')
            for i in p:
                list_of_doctors[i]=i.clinic_fee
            #filter="Clinics"
            print(filter_type)
            print(p)
            if (len(p) == 0):
                messages.info(request, "No Clinic Available")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_doctors": list_of_doctors, "filter": filter,
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
            print(p)
            if(len(p)==0):
                messages.info(request, "No Clinic Available of this name")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_doctors": p, "filter": filter,"search_value":search_value,
                                   'list_of_countries': lis_of_countries, "list_of_tests": list_of_tests,
                                   "list_of_speciality": list_of_speciality})

        elif(filter_type=='Location'):
            Country=request.GET.get("country").strip()
            City=request.GET.get("city").strip()
            State=request.GET.get("state").strip()
            print(City,State,Country)
            request.session['city']=City
            request.session['state']=State
            request.session['country']=Country
            location = City + ',' + State + ',' + Country
            print(City,Country)
            p=Hospital.objects.filter(country__iexact=Country.strip()).filter(city__iexact=City.strip()).filter(verified="Yes")
            #filter="Hospital"
            if (len(p) == 0):
                messages.info(request, "No Hospital available in this area")
        elif (filter_type == 'Doctor_Name'):
            p = {}
            search_value = request.GET.get("search_values")
            if(country==""):
                k=Doctor.objects.filter(verified="Yes")
            else:
                k=Doctor.objects.filter(verified="Yes").filter(country=country).filter(city=city)
            for i in k:
                s1=search_value.casefold()
                s2=i.doctorid.name.casefold()
                if (s2.find(s1)!=-1):#i.doctorid.name.casefold() == search_value.casefold()):
                    if(i.clinic_name==''):
                        k1=HospitalSpeciality.objects.filter(hospitalid=i.hospitalid).filter(speciality=i.specialization)
                        p[i]=k1[0].price
                    else:
                       p[i]=i.clinic_fee

            #print(p,search_value)
            if(len(p)==0):
                messages.info(request, "No Doctor of this name")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_doctors": p,"filter":filter,"search_value":search_value, 'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
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
                messages.info(request,"No Hospital Available with this Name")
            return render(request, "main_app/Hospital_Selection.html",
                          context={"location":location,"list_of_hospitals": p,"search_value":search_value, "filter": filter, 'list_of_countries': lis_of_countries,
                                   "list_of_tests": list_of_tests, "list_of_speciality": list_of_speciality})
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
                messages.info(request,"No Testing lab available with this name")

            return render(request, "main_app/Hospital_Selection.html",
                                  context={"location":location,"list_of_testing_labs": p, "filter": filter,"search_value":search_value,
                                           'list_of_countries': lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
        return render(request,"main_app/Hospital_Selection.html",context={"location":location,"list_of_hospitals":p,"filter":filter,'list_of_countries':lis_of_countries,"list_of_tests":list_of_tests,"list_of_speciality":list_of_speciality})
     #except:
     #   return redirect("/Hospital_Selection/")

def Selected_Service_Provider(request,user_id):
    user=UserDetails.objects.get(userid=user_id)
    request.session['user_type_Id']=int(user_id)
    print(user.user_type)
    if(user.user_type=="Hospital"):
        p = Hospital.objects.get(hospitalid=user_id)
        k=HospitalSpeciality.objects.filter(hospitalid=p)
        k1=Hospital_News.objects.filter(hospitalid=p)
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
        return render(request,"main_app/Dashboard.html",context={"Hospital_News":k1,"Hospital_Details":p,"specialities":dict1})
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
    Appointment_Id=request.POST['Appointment_Id']
    prescription = request.FILES['prescription']
    b1=Appointments.objects.get(appointmentid=int(Appointment_Id))
    b1.Prescription=prescription
    b1.save()
    return redirect("/profile")
    #return render(request,"main_app/Profile.html",context={"list_of_Appointments":dict})
def Payment(request):
            print(request.GET['time_slot'])
            try:
                email = request.session['email']
            except:
                messages.info(request,"Please Login/Register")
                return redirect('/')
            service_provider_id=request.GET['service_provider_id']
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
                print(appointment_time)
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
def cancel_appointment(request):
    messages.info(request,"Appointment Canceled Sucessfully")
    return redirect('/Hospital_Selection')

def change_date(request):
    request.session['date']=request.POST['date']
    service_provider = UserDetails.objects.get(userid=request.session['doctorid'])
    if(service_provider.user_type=="Testing Lab"):
        User_Profile = TestingLab.objects.get(tlabid=request.session['doctorid'])
    else:
        User_Profile=Doctor.objects.get(doctorid=request.session['doctorid'])
    slots=available_slots(service_provider,request.session['date'])
    return render(request, "main_app/Profile1.html",
                      context={"date": request.session['date'], "User_Profile": User_Profile, 'slots': slots})

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
                    print(d12)
                    da = datetime.datetime(int(d12[0]), int(d12[1]), int(d12[2]), int(t12[0]), int(t12[1]), int(t12[2]))
                    slots.append(da)

    else:
        p13=UserDetails.objects.get(userid=service_provider.userid)
        if(p13.user_type=="Doctor"):
            d1=Doctor.objects.get(doctorid=service_provider)
            start_time=d1.start_time.split(":")
            end_time=d1.end_time.split(":")
            print(start_time,end_time)
        else:
            """t1 = TestingLab.objects.get(tlabid=service_provider)
            start_time = t1.start_time.split(":")
            end_time = t1.end_time.split(":")
            print(start_time, end_time)"""
            start_time=[9,0,0]
            end_time=[16,0,0]
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
            user = UserDetails.objects.get(userid=request.session['user_type_Id'])
            doctordetails=""
            if(user.user_type=="Hospital" or user.user_type=="Doctor"):
                a1=Appointments()
                mode=request.session['mode']
                doctorid=request.session['doctorid']
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
                print(b1[0])
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
                print(len(b1))
                b1.update(Booked=True)
                a1.save()

            return render(request,"main_app/Receipt.html",context={"Appointment_Details":a1,"service_provider":user,"doctor_details":doctor_details})
    #except:
    #    return redirect("/Doctor/")

def select_speciality(request,service_provider_id):
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
        return render(request,"main_app/List_Of_Speciality.html",context={"date":date,"specialities":Specialities,"Hospital_Details":p})
    elif(user.user_type=="Testing Lab"):
        p = TestingLab.objects.get(tlabid=service_provider_id)
        k = TestPricing.objects.filter(tlabid=service_provider_id)
        Tests = []
        for i in k:
            Tests.append(i.testname)
        return render(request, "main_app/List_Of_Speciality.html", context={"date":date,"Testing_Lab_Details": p, "specialities": Tests})
def book_appointment1(request,speciality,service_provider_id):
    user=UserDetails.objects.get(userid=service_provider_id)
    request.session['speciality'] = speciality
    if(user.user_type=="Hospital"):
        p=Doctor.objects.filter(specialization=speciality).filter(hospitalid=service_provider_id).filter(verified="Yes")
        list_of_doctors=[]
        for i in p:
            #user1=User.objects.get()
            t=Appointment_Timings.objects.filter(service_provider_id=i.doctorid).filter(date=request.session['date'])
            print(len(t))
            if len(t)==0:
                list_of_doctors.append(i)
            else:
                #print(t[0].Slots_Booked)
                print("availabel",t[0].available)
                if(t[0].available==True):
                    list_of_doctors.append(i)
                    #list_of_doctors[i] = time_slots.split(",")
        k = Hospital.objects.get(hospitalid=user.userid)
        return render(request, "main_app/Select_Doctor.html", context={"list_of_Doctors": list_of_doctors,"Hospital_Details":k})

def Appointment_Details_Submission1(request):
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
                print(request.GET['doctorid'])
                service_provider = UserDetails.objects.get(userid=int(request.GET['doctorid']))
                User_Profile=Doctor.objects.get(doctorid=int(request.GET['doctorid']))

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

        return render(request, "main_app/Profile1.html", context={"date":request.session['date'],"User_Profile": User_Profile, 'slots': slots})


def chosen_date(request):
    request.session['date']=request.GET.get("date")
    print(request.GET.get("date"))
    return JsonResponse(request.session['date'],safe=False)

def user_location(request):
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

    print(request.session['city'])
    #print(address)
    return JsonResponse(request.GET['longitude'], safe=False)

def search_appointments(request):
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
                            patientname__iexact=search_values)
                return render(request, 'main_app/Profile.html',
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
            return render(request, 'main_app/Profile.html',
                          context={"available": available, "dict_test": no_of_test_appointments,
                                   "Test_Names": json.dumps(tests),
                                   "list_of_Appointments": appoin(list_of_Appointments), "User_Details": User_Profile,
                                   "no_of_Appointments_completed": no_of_Appointments_completed,
                                   "no_of_Appointments": no_of_Appointments,"filter_type":filter_type,"search_value":search_values})
            # print(p)

    #except:
     #   return redirect('/profile')
def Appointment_Details(request,appointment_id):
    Appointment_Details1=Appointments.objects.get(appointmentid=appointment_id)
    return render(request,'main_app/Receipt.html',context={'Appointment_Details':Appointment_Details1})

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
            l12 = Appointment_Timings.objects.filter(service_provider_id=i.doctorid.userid).filter(date=dt)
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

    print(list_of_speciality)
    filter_type = request.GET['filter']
    Appointments1 = []
    if (filter_type == "speciality"):

        search_values = request.GET['search_values1']
    else:
        search_values = request.GET['search_values']

    print(search_values)
    for i in list_of_doctors:
            print(i.doctorid.email)
            if (filter_type == "Date"):
                    p1=Appointments.objects.filter(appointment_date=search_values).filter(doctoremail=i.doctorid.email)
                    for j in p1:
                        Appointments1.append(j)
            elif (filter_type == "Doctor_Name"):
                doctor = UserDetails.objects.filter(name__iexact=search_values).filter(user_type="Doctor")
                for j in doctor:
                    Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(doctoremail=j.email)
                break;
            elif(filter_type=="Patient_Name"):
                Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(patientname__iexact=search_values)
                break;
            elif(filter_type=="speciality"):
                Appointments1 = Appointments.objects.filter(appointment_date=dt).filter(
                    Speciality=search_values)
                break;
    print(Appointments1)
    return render(request, "main_app/Admin_Dashboard.html",
                  context={"filter_type":filter_type,"search_value":search_values,"speciality":speciality,"list_of_Appointments": Appointments1, "doctors_data": doctors_data,
                           "list_of_speciality": json.dumps(list(list_of_speciality.keys())),"hospitalid":user.userid,
                           "list_of_speciality_appointments": list(list_of_speciality.values()),
                           "Online_consultations_today": Online_consultations_today,
                           "appointments_this_month": appointments_this_month, "earning_this_month": earning_this_month,
                           "appointments_today": appointments_today,"filter_type":filter_type,"search_value":search_values})


def availablity(request):
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
    print(start,end)
    if (user.user_type == "Doctor"):
        d1 = Doctor.objects.get(doctorid=user.userid)
        start_time = d1.start_time.split(":")
        end_time = d1.end_time.split(":")
        print(start_time, end_time)
    else:
        t1 = TestingLab.objects.get(tlabid=user.userid)
        start_time = t1.start_time.split(":")
        end_time = t1.end_time.split(":")
        print(start_time, end_time)
    user_start_time = datetime.datetime(int(start[0]), int(start[1]), int(start[2]), int(start_time[0]), int(start_time[1]), 0)
    user_end_time=datetime.datetime(int(start[0]), int(start[1]), int(start[2]), int(end_time[0]), int(end_time[1]), 0)
    while(user_start_time<=end1):
        if(user.user_type=="Testing Lab"):
            tester=TestingLab.objects.get(tlabid=user.userid)
            service_provider=UserDetails.objects.get(userid=user.userid)
            print(Appointment_Timings.objects.filter(service_provider_id=service_provider).filter(
                date=user_start_time.date()).delete())
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
            print(Appointment_Timings.objects.filter(service_provider_id=service_provider).filter(date=user_start_time.date()).delete())
            print()
            if (user_start_time > start1 and user_end_time < end1):

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

    return redirect("/profile")

def cancel_appointments(list_of_appointments,user):
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

def report(request):
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
    print(list_of_speciality)
    return render(request, "main_app/Admin_Dashboard1.html",
                  context={"speciality": speciality, "list_of_Appointments": Appointments1,
                           "doctors_data": doctors_data,
                           "start":start,"end":end,
                           "list_of_speciality": json.dumps(list(list_of_speciality.keys())),
                           "list_of_speciality_appointments": list(list_of_speciality.values()),
                           "Online_consultations_today": Online_consultations_today,
                           "appointments_this_month": appointments_this_month, "earning_this_month": earning_this_month,
                           "appointments_today": appointments_today})

def add_news(request,id):
    return render(request,"main_app/News.html",context={"id":id})

def submit_news(request):
    a1=Hospital_News()
    a1.Title=request.POST['title']
    a1.photos=request.FILES['file1']
    a1.Information=request.POST['About']
    a1.hospitalid=Hospital.objects.get(hospitalid=request.POST['id'])
    a1.save()
    return redirect('profile')


"""
while(date<=end1):
        date1=date.date()
        if(user.user_type=="Testing Lab"):
            tester=TestingLab.objects.get(tlabid=user.userid)
            l2 = Appointments.objects.filter(appointment_date=date1).filter(TestingLabId=tester)
            p1=Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=date1)
            if(len(p1)>0):
                a1=p1[0]
            else:
                a1 = Appointment_Timings()
            a1.service_provider_id=user
            a1.available=False
            a1.date=date
            a1.save()
            for i in l2:
                list_of_appointments.append(i)
        elif(user.user_type=="Doctor"):
            doctor = Doctor.objects.get(doctorid=user.userid)
            l2 = Appointments.objects.filter(appointment_date=date1).filter(doctoremail=user.email)
            p1 = Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=date1)
            if (len(p1) > 0):
                a1 = p1[0]
            else:
                a1 = Appointment_Timings()
            a1.service_provider_id = user
            a1.available = False
            a1.date = date
            a1.save()
            for i in l2:
                list_of_appointments.append(i)
        date += datetime.timedelta(days=1)
        cancel_appointments(list_of_appointments,user)
    return redirect("/profile")
"""
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
        user=UserDetails.objects.get(userid=i.doctorid.userid)
        #print(Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count())
        l2 = Appointments.objects.filter(appointment_date__month=dt.month).filter(doctoremail=i.doctorid.email).count()
        list_of_speciality[i.specialization]+=l2
        p1=HospitalSpeciality.objects.filter(speciality=i.specialization).filter(hospitalid=16)
        if(len(p1)==0):
            l1.append(0)
            l12 = Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=dt)
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
                l12=Appointment_Timings.objects.filter(service_provider_id=user.userid).filter(date=dt)

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
    return render(request, "main_app/Admin_Dashboard.html",context={"hospitalid":16,"speciality":speciality,"list_of_Appointments":Appointments1,"doctors_data":doctors_data,"list_of_speciality":json.dumps(list(list_of_speciality.keys())),"list_of_speciality_appointments":list(list_of_speciality.values()),"Online_consultations_today":Online_consultations_today,"appointments_this_month":appointments_this_month,"earning_this_month":earning_this_month,"appointments_today":appointments_today})