import time
from main_app.models import*;
from django.contrib import messages
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
def verify(request):
    #email = request.session['email']
    user=UserDetails.objects.get(email=request.session['email'])
    p=dict()
    if(user.user_type=='Moderator'):
        p['Hospital']=Hospital.objects.filter(verified="No")
    #p['Clinic']=Hospital.objects.filter(verified="No").filter(clinic_name=)
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
        p['Hospital'] = Hospital.objects.filter(verified="Yes")
        # p['Clinic']=Hospital.objects.filter(verified="No").filter(clinic_name=)
        p['Doctor'] = Doctor.objects.filter(verified="Yes")
        p['Testing_Lab'] = TestingLab.objects.filter(verified="No")
        return render(request, "main_app/Verify_Certificate.html", context={'list_of_certificates': p})
    else:
        messages.info(request, "You Can't Access This Page!")
        return redirect("/")

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

                list_of_Appointments = Appointments.objects.filter(patientemail=email).order_by('-appointment_date')
                User_Profile=i
                break;
        list_of_Appointments = Appointments.objects.filter(patientemail=email)
    if (user_type == 'Doctor'):
        for i in Doctor.objects.all():
            #print(type(i.doctorid.userid))
            if(i.doctorid==user):
                User_Profile=i
                list_of_Appointments =Appointments.objects.filter(doctoremail=i.doctorid.email).order_by('-appointment_date')
                #print(p)
                break;
    #print(p)
                list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email)
                break
    print(list_of_Appointments)
    for i in list_of_Appointments:
        print(i.Prescription)
        if (i.Prescription!=""):
            dict[i] = i
        else:
            dict[i] = "Upload Prescription"
    print(dict)
    return render(request, 'main_app/Profile.html',
                      context={"list_of_Appointments": dict, "User_Details": User_Profile})

def index(request):
    return render(request,'main_app/index.html')
def home(request):
    return render(request,'main_app/home.html')

def Hospitals(request):
    lis_of_countries = geo_plug.all_CountryNames()
    p=Hospital.objects.filter(verified="Yes")
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
        #print("ppp:",filter_type)
        filter1=''
        if(filter_type=='Hospitals'):
            p = Hospital.objects.all()
            filter="Hospitals"
        elif(filter_type=='Testing_Labs'):
            p=TestingLab.objects.all()
            filter="Testing_Labs"
        if(filter_type=='Location'):
            Country=request.POST.get("country")
            City=request.POST.get("city")
            State=request.POST.get("state")
            p=Hospital.objects.filter(country=Country).filter(city=City).filter(verified="Yes")
            print(p)
        elif (filter_type == 'Doctor_Name'):
            p = []
            search_value = request.POST.get("search_values")
            for i in Doctor.objects.all():
                if (i.doctorid.name == search_value):
                    p.append(i)
                    break;
            #print(p,search_value)
            return render(request, "main_app/Hospital_Selection.html",
                          context={"list_of_doctors": p,"filter":"Doctor", 'list_of_countries': lis_of_countries})
        elif(filter_type=='Hospital_Name'):
            p=[]
            search_value=request.POST.get("search_values")
            for i in Hospital.objects.all():
                if(i.hospitalid.name==search_value):
                    p.append(i)
                    break;
        elif(filter_type=='Testing_Lab'):
            search_value = request.POST.get("search_values")
            p=[]
            for i in TestingLab.objects.all():
                if(i.tlabid.name==search_value):
                    p.append(i)
                    break;
        return render(request,"main_app/Hospital_Selection.html",context={"list_of_hospitals":p,"filter":filter,'list_of_countries':lis_of_countries})

    except:
        return redirect("/Doctor/")

def Selected_Service_Provider(request,hospital_id):
    p = Hospital.objects.get(hospitalid=hospital_id)
    request.session['Hospital_Id']=hospital_id
    k=HospitalSpeciality.objects.filter(hospitalid=p)
    Specialities=[]
    for i in k:
        Specialities.append(i.speciality)
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
    """for i in Patient.objects.all():
        if(i.patientid.email=="ram12@gmail.com"):
            b1 = Patient.objects.filter(patientid=12)
            b1.update(Prescription=prescription)"""
    for i in Doctor.objects.all():
        # print(type(i.doctorid.userid))
        if (i.doctorid.email == request.session['email']):
            Doctor_Details = i
            list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email)
            break
    for i in list_of_Appointments:
        #p=UserDetails.objects.get(email=i.patientemail)
        #k=Patient.objects.get(patientid=12)
        print(i.Prescription)
        if(i.Prescription!=''):
            dict[i]=i
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
            if(i.doctorid.userid==int(doctorid)):
                a1.doctoremail=i.doctorid.email
                doctor_details=i
        a1.amount_paid=250
        if(request.POST['date']!=None):
            a1.appointment_date=request.POST['date']
        else:
            a1.appointment_date=request.session["date"]
        t = Appointment_slots.objects.filter(doctorid=doctorid).filter(date=request.session['date'])
        no_of_slots_booked_already=0

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

        return redirect("/Doctor/")

def select_speciality(request):
    p = Hospital.objects.get(hospitalid=request.session['Hospital_Id'])
    k = HospitalSpeciality.objects.filter(hospitalid=p)
    Specialities = []
    for i in k:
        Specialities.append(i.speciality)
    return render(request,"main_app/List_Of_Speciality.html",context={"specialities":Specialities,"Hospital_Details":p})

def book_appointment1(request,speciality):
    p=Doctor.objects.filter(specialization=speciality).filter(hospitalid=request.session['Hospital_Id']).filter(verified="Yes")
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
def search_appointments(request):
    #try:
        email = request.session['email']
        filter_type=request.POST['filter']
        search_values=request.POST['search_values']
        dict = {}
        for i in UserDetails.objects.all():
            if (i.email == email):
                user_id = i.userid
                user = i
                user_type = i.user_type
        print(user_id)
        if (user_type == 'Patient'):
            for i in Patient.objects.all():
                if (i.patientid == user):
                    User_Profile = i;
                    break;
            if(filter_type=='Date'):
                list_of_Appointments = Appointments.objects.filter(patientemail=email).filter(appointment_date=search_values)
            else:
                list_of_Appointments=[]
                lis_of_doctors=UserDetails.objects.filter(user_type="Doctor").filter(name__iexact=search_values)
                for i in lis_of_doctors:
                    list_of_Appointments=Appointments.objects.filter(patientemail=email).filter(doctoremail__iexact=i.email)
                    for j in list_of_Appointments:
                        if (j.Prescription != ""):
                            dict[j] = j
                        else:
                            dict[j] = "Upload Prescription"

        if (user_type == 'Doctor'):
            for i in Doctor.objects.all():
                # print(type(i.doctorid.userid))
                if (i.doctorid == user):
                    User_Profile = i
                    if (filter_type == 'Date'):
                        list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter( appointment_date=search_values)
                    else:
                        list_of_Appointments = Appointments.objects.filter(doctoremail=i.doctorid.email).filter(
                            patientname__iexact=search_values)


                    # print(p)
                    break;
        # print(p)
        if(user_type!="Patient"):
            for i in list_of_Appointments:
                if (i.Prescription != ""):
                    dict[i] = i
                else:
                    dict[i] = "Upload Prescription"
            print(dict)
        return render(request, 'main_app/Profile.html',
                      context={"list_of_Appointments": dict, "User_Details": User_Profile})
    #except:
    #    return redirect('/profile')
def Appointment_Details(request,appointment_id):
    Appointment_Details1=Appointments.objects.get(appointmentid=appointment_id)
    return render(request,'main_app/Receipt.html',context={'Appointment_Details':Appointment_Details1})

