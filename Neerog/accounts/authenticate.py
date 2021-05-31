from django.contrib.auth.models import User,auth
from main_app.models import UserDetails, Doctor, Patient, Hospital, HospitalSpeciality, TestingLab, TestPricing
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from . import tokens
import sys
from main_app import domain

def sendConfirmEmail(user,name,userEmail):
    template=render_to_string('accounts/email_template.html',
        {
            'name':name,
            'user':user,
            'token':tokens.account_token.make_token(user),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'domain': domain.getDomainName(),
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
        return None
    else:
        username=userobj.userid
        user=auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            return username
        else:
            return None

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
        print(sys.exc_info())
        return False

def registerDoctor(uid, start_time, end_time, phone, is_independent, gender, experience, specialization, proof, hospitalid, cname, cphoto, fee, country, state, city, area, zip):
    try:
        userobj=UserDetails.objects.get(userid=uid)
        if hospitalid is not None:
            hospitalid=Hospital.objects.get(hospitalid=hospitalid)

        doctor=Doctor(doctorid=userobj,start_time=start_time, end_time=end_time, phone=phone, is_independent=is_independent, gender=gender, experience=experience, specialization=specialization, certificate=proof, clinic_name=cname, clinic_photo = cphoto, country=country, state=state, city=city, zip=zip, area=area, hospitalid=hospitalid, clinic_fee=fee)
        doctor.save()
        return True
    except:
        print(sys.exc_info())
        return False

def registerHospital(uid, phone, country, state, city, zip, area, speciality_pricing, pic1, certificate):
    try:
        userobj=UserDetails.objects.get(userid=uid)
        hospital=Hospital(hospitalid=userobj, phone=phone, country=country, state=state, city=city, zip=zip, area=area, pic1=pic1, certificate=certificate)
        hospital.save()
        for sp in speciality_pricing:
            hospitalspeciality = HospitalSpeciality(hospitalid=hospital, speciality = sp, price=speciality_pricing[sp])
            hospitalspeciality.save()
        return True
    except:
        print(sys.exc_info())
        return False


def registerTLab(uid, phone, country, state, city, zip, area, test_pricing, pic1, certificate):
    try:
        userobj=UserDetails.objects.get(userid=uid)
        tlab=TestingLab(tlabid=userobj, phone=phone, country=country, state=state, city=city, zip=zip, area=area, lab_photo=pic1, certificate=certificate)
        tlab.save()
        for sp in test_pricing:
            testpricing = TestPricing(tlabid=tlab, testname = sp, price=test_pricing[sp])
            testpricing.save()
        return True
    except:
        print(sys.exc_info())
        return False

def registerPatient(uid, phone, country, state, city, area, zip, gender, age, disability, profilepic):
    try:
        userobj=UserDetails.objects.get(userid=uid)
        patient=Patient(patientid=userobj, phone=phone, country=country,state=state, city=city, area=area, zip=zip, gender=gender, age=age, disability=disability, profile_pic=profilepic)
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
        elif user_type=="Hospital":
            Hospital.objects.get(phone=phone)
            return True
        elif user_type=="Patient":
            Patient.objects.get(phone=phone)
            return True
        elif user_type=="Testing Lab":
            TestingLab.objects.get(phone=phone)
            return True
        else:
            return False
    except:
        return False