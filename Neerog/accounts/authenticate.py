from django.contrib.auth.models import User,auth
from main_app.models import UserDetails, Doctor, Patient, Hospital
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from . import tokens
import sys


def getUserType(uid):
    userobj=UserDetails.objects.get(userid=uid-1)
    return str(userobj.user_type)

def isVerifiedUser(uid):
    user_type=getUserType(uid)
    if(user_type == "Doctor"):
        try:
            doctorobj=Doctor.objects.get(doctorid=uid-1)
            if(str(doctorobj.verified) == "No"):
                return False
            else:
                return True
        except:
            return False
    elif(user_type == "Hospital"):
        try:
            hospitalobj=Hospital.objects.get(hospitalid=uid-1)
            if(str(hospitalobj.verified) == "No"):
                return False
            else:
                return True
        except:
            return False
    elif(user_type == "Patient"):
        try:
            patientobj=Patient.objects.get(patientid=uid-1)
            return True
        except:
            return False



def sendConfirmEmail(user,name,userEmail):
    template=render_to_string('accounts/email_template.html',
        {
            'name':name,
            'user':user,
            'token':tokens.account_token.make_token(user),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'domain': '127.0.0.1:8000',
        })
    email = EmailMessage(
        "Confirm Your Neerog Account",
        template,
        settings.EMAIL_HOST_USER,
        [userEmail],
    )
    email.fail_silently=False
    email.send()

def login(request,email, password):
    try:
        userobj=UserDetails.objects.get(email=email)
    except:
        userobj=None
    if userobj is None:
        return False
    else:
        username=userobj.userid
        user=auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            return True
        else:
            return False

def register(name,user_type,password,email):
    try:
        userdetails=UserDetails(name=name,user_type=user_type,email=email)
        userdetails.save()
        user=User.objects.create_user(username=userdetails.userid,password=password,email=email)
        user.is_active=False
        user.save()
        sendConfirmEmail(user,name,email)
        return True
    except:
        print(sys.exc_info()[0], "occurred!")
        return False

def registerDoctor(uid, phone, is_independent, gender, experience, specialization, institution, proof):
    try:
        clinic_name = ""
        if(is_independent == "True"):
            is_independent = True
            clinic_name = institution
        else:
            is_independent = False
            # hospitalid = hospital_object
        userobj=UserDetails.objects.get(userid=uid-1)
        doctor=Doctor(doctorid=userobj, phone=phone, is_independent=is_independent, gender=gender, experience=experience, specialization=specialization, certificate=proof, clinic_name=clinic_name)
        doctor.save()
        return True
    except:
        print(sys.exc_info())
        return False

def registerPatient(uid, phone, country, city, gender, age, disability, profilepic):
    try:
        userobj=UserDetails.objects.get(userid=uid-1)
        patient=Patient(patientid=userobj, phone=phone, country=country, city=city, gender=gender, age=age, disability=disability, profile_pic=profilepic)
        patient.save()
        return True
    except:
        print(sys.exc_info())
        return False

def hasRegisteredEmail(email):
    try:
        UserDetails.objects.get(email=email)
        return True
    except:
        return False

def hasRegisteredPhone(phone, user_type):
    try:
        if user_type=="Doctor":
            Doctor.objects.get(phone=phone)
            return True
        elif user_type=="Patient":
            Patient.objects.get(phone=phone)
            return True
        else:
            return False
    except:
        return False