import time
from main_app.models import *;
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
from Neerog import secret_settings
import random
# render syntax:
# return render(request,'page.html',context_var_dictionary)

# Create your views here.

replace_dictionary={"u0101":"a","u012b":"i","u016b":"u","u0100":"A","u016a":"u"}

def profile(request):
    email=request.session['email']
    dict={}
    for i in UserDetails.objects.all():
        if(i.email==email):
            user_id=i.userid
            user=i
            user_type=i.user_type
    print(user_id)
    if(user_type=='Patient'):
        for i in Patient.objects.all():
            if (i.patientid==user):
                User_Profile=i;
                break;
        list_of_Appointments = Appointments.objects.filter(patientemail=email)
    if (user_type == 'Doctor'):
        for i in Doctor.objects.all():
            #print(type(i.doctorid.userid))
            if(i.doctorid.userid==10):
                print(i.doctorid)
                User_Profile=i
                list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email)
                break;
    print(list_of_Appointments)
    for i in list_of_Appointments:
            p = UserDetails.objects.get(email=i.patientemail)
            #print("userdetails",p)
            #k = Patient.objects.get(patientid=p)
            #print(k.Prescription)
            #if (k.Prescription != None):
            #    dict[i] = k
            #else:
            dict[i] = "Upload Prescription"
    return render(request, 'main_app/Profile.html',
                      context={"list_of_Appointments": dict, "User_Details": User_Profile})

def index(request):
    return render(request,'main_app/index.html')
def home(request):
    return render(request,'main_app/home.html')

def Hospitals(request):
    lis_of_countries = geo_plug.all_CountryNames()
    p=Hospital.objects.all()
    for i in p:
        print(i.pic1,i.hospitalid.name,i.city)
    request.session['Username'] = 10
    return render(request,'main_app/Hospital_Selection.html',context={'list_of_countries':lis_of_countries,"list_of_hospitals":p})


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
    duration=30; # Duration of Zoom meeting
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
    encoded = create_jwt_token();
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
    l=0;
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
    t=0;
    for i in lis_of_cities:
        str1=i.replace("\\","");
        #print(str1)
        for key,value in replace_dictionary.items():
            if(str1.find(key)!=-1):
                str1=str1.replace(key,value)
        list_of_cities.append(str1)
    return JsonResponse(data=list_of_cities, safe=False)

def list_of_hospital(request):
    Country=request.POST.get("country")
    City=request.POST.get("city")
    State=request.POST.get("state")
    lis_of_countries = geo_plug.all_CountryNames()
    p=Hospital.objects.filter(country=Country).filter(city=City)

    return render(request,"main_app/Hospital_Selection.html",context={"list_of_hospitals":p,'list_of_countries':lis_of_countries})

def Selected_Service_Provider(request,hospital_id):
    p = Hospital.objects.get(hospitalid=hospital_id)
    request.session['Hospital_Id']=hospital_id
    Specialities=p.speciality.split(",")
    dict1={}
    poke = pd.read_csv("E:\\IIT Research Project\\Neerog_website\\Project\\Neerog\\main_app\\static\\Specialities_Images.csv")
    list1 =poke['Speciality'].tolist()
    list2=poke['Speciality_Image'].tolist()
    print(list1,list2)
    for i in Specialities:
        if i in list1:
            dict1[i]=list2[list1.index(i)]
    return render(request,"main_app/Dashboard.html",context={"Hospital_Details":p,"specialities":dict1})
def Book_Appointment(request):
    return render(request,"main_app/Book_Appointment.html",context={"Doctor":replace_dictionary,"specialities":Specialities,"facilities":Facilities})

def Add_Prescription(request):

    Patient_Email=request.POST['Email']

    return render(request,"main_app/Prescription.html",context={"Patient_Email":Patient_Email})

def submit_Prescription(request):
    email = request.POST['Email']
    dict={}
    prescription = request.FILES['prescription']
    print(prescription)
    #b1 = Patient.objects.filter(doctorid=doctor_details).filter(date=request.session['date'])
    for i in Patient.objects.all():
        if(i.patientid.email=="ram12@gmail.com"):
            b1 = Patient.objects.filter(patientid=12)
            b1.update(Prescription=prescription)
    for i in Doctor.objects.all():
        # print(type(i.doctorid.userid))
        if (i.doctorid.userid == 10):
            print(i.doctorid)
            Doctor_Details = i
            list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email)
            break;
    for i in list_of_Appointments:
        p=UserDetails.objects.get(email=i.patientemail)
        k=Patient.objects.get(patientid=12)
        if(k.Prescription!=None):
            dict[i]=k
        else:
            dict[i] = "Upload Prescription"

    return render(request,"main_app/Profile.html",context={"list_of_Appointments":dict})

def Appointment_Details_Submission(request):
    try:
        a1=Appointments()
        mode=request.POST['mode']
        doctorid=request.POST['doctorid']
        email=request.session['email']
        for i in UserDetails.objects.all():
            if(i.email==email):
                a1.patientname=i.name
                a1.patientemail=i.email
        a1.Speciality=request.session['speciality']
        for i in Doctor.objects.all():
            #print(type(i.doctorid.userid))
            if(i.doctorid.userid==10):
                a1.doctoremail=i.doctorid.email
                doctor_details=i;
        a1.amount_paid=250
        a1.appointment_date=request.session["date"]
        t = Appointment_slots.objects.filter(doctorid=doctorid).filter(date=request.session['date'])
        no_of_slots_booked_already=0;

        if len(t) > 0:
            no_of_slots_booked_already=t[0].Slots_Booked
            if no_of_slots_booked_already%2==0:
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
           a1.meeting_url=create_zoom_meeting(request.session['date'],t1)
           a1.mode_of_meeting = mode
        else:
            a1.mode_of_meeting = mode
        a1.save()
        b1=Appointment_slots.objects.filter(doctorid=doctor_details).filter(date=request.session['date'])
        if len(b1)>0:
            b1.update(Slots_Booked=no_of_slots_booked_already+1)
        else:
            b1=Appointment_slots()
            b1.doctorid=doctor_details
            b1.date=request.session["date"]
            b1.Slots_Booked=1
            b1.save()
        return render(request,"main_app/Receipt.html",context={"Appointment_Details":a1})
    except:
        return redirect("/select_speciality/")

def select_speciality(request):
    p = Hospital.objects.get(hospitalid=request.session['Hospital_Id'])
    Specialities = p.speciality.split(",")
    return render(request,"main_app/List_Of_Speciality.html",context={"specialities":Specialities,"Hospital_Details":p})

def book_appointment1(request,speciality):
    p=Doctor.objects.filter(specialization=speciality)
    #t=Appointment_slots. vfv,mflv.filter(date=request.session['date']).filter(Slots_Booked < 16)
    list_of_doctors=[]
    for i in p:
        t=Appointment_slots.objects.filter(doctorid=i).filter(date=request.session['date'])
        if len(t)==0:
            list_of_doctors.append(i)
        else:
            print(t[0].Slots_Booked)
            if(t[0].Slots_Booked < 3):
                list_of_doctors.append(i)

    k = Hospital.objects.get(hospitalid=request.session['Hospital_Id'])
    request.session['speciality']=speciality
    return render(request, "main_app/Select_Doctor.html", context={"list_of_Doctors": list_of_doctors,"Hospital_Details":k})

def chosen_date(request):
    request.session['date']=request.GET.get("date")
    print(request.GET.get("date"))
    return JsonResponse(request.session['date'],safe=False)