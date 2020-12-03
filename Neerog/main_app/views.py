import time

import requests
import json
import re
import json
from django.http import HttpResponse, JsonResponse
from geosky import geo_plug # library for geolocation
import datetime
import jwt
from django.shortcuts import render
from Neerog import secret_settings
import random
# render syntax:
# return render(request,'page.html',context_var_dictionary)

# Create your views here.
def index(request):
    return render(request,'main_app/index.html')
def home(request):
    return render(request,'main_app/home.html')
def doctor_dashboard(request):
    lis_of_countries = geo_plug.all_CountryNames();
    return render(request,'main_app/Hospital_Selection.html',context={'list_of_countries':lis_of_countries})

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
def create_zoom_meeting(request):
    url = "https://api.zoom.us/v2/users/"+secret_settings.email_host_user+"/meetings"
    password=random.randint(0,999999) #Password of Zoom meeting
    duration=30; # Duration of Zoom meeting
    k=datetime.datetime.now()
    start_time=str(k.year)+"-"+str(k.month)+"-"+str(k.day)+"T"+str(k.hour)+":"+str(k.minute)+":"+str(k.second) # StartTime for zoom meeting
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
    print(jsonResponse)
    return render(request,"main_app/Profile.html",context={'meeting_url':jsonResponse['join_url'],'meeting_id':jsonResponse['id'],'meeting_password':jsonResponse['password']})

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
    return JsonResponse(data=lis_of_states,safe=False)

def list_of_city(request):
    state=request.GET.get("city")
    state=re.sub("\"","",state).strip()
    print(state)
    city = geo_plug.all_State_CityNames(str(state))
    k = city.split(":")
    trailing =re.sub("\"", "", k[1])
    trailing=re.sub("}","",re.sub("\]","",re.sub("\[","",trailing))).strip()
    lis_of_cities = trailing[1:len(trailing) - 2].split(",")
    lis_of_cities=re.sub("\]","",re.sub("\'","",re.sub("\[","",str(lis_of_cities))))
    return JsonResponse(data=lis_of_cities, safe=False)

def list_of_hospital(request):
    Country=request.POST.get("country")
    City=request.POST.get("city")
    State=request.POST.get("state")
    return HttpResponse(Country+City+State)

