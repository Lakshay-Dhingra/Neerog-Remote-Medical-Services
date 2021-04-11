from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from . import tokens
from . import authenticate
from main_app import user_data, location
from main_app import medical_speciality, medical_tests
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# render syntax:
# return render(request,'page.html',context_var_dictionary)

def logout(request):
    auth.logout(request)
    for key in request.session.keys():
        del request.session[key]
    messages.info(request,"Logged Out Successfully!")
    return redirect("/")

def signin(request):
    return render(request,'accounts/signin.html')

def signup(request):
    return render(request,'accounts/signup.html')

def signup_redirect(request):
    if(user_data.getUserType(request.user.id) == "Doctor"):
        return redirect("/accounts/signup/doctor")
    elif(user_data.getUserType(request.user.id) == "Patient"):
        return redirect("/accounts/signup/patient")
    elif(user_data.getUserType(request.user.id) == "Hospital"):
        return redirect("/accounts/signup/hospital")
    elif(user_data.getUserType(request.user.id) == "Testing Lab"):
        return redirect("/accounts/signup/testinglab")

def signup_doctor(request):
    if(user_data.getUserType(request.user.id) == "Doctor"):
        if(user_data.isVerifiedUser(request.user.id)):
            messages.info(request,"You're Details Have Already Been Submitted!")
            return redirect("/")
        else:
            data={'specialities':medical_speciality.get_specialities()}
            data['countries']=location.getCountries()
            return render(request,'accounts/signup_doctor.html',data)
    else:
        messages.info(request,"You Can't Access This Page!")
        return redirect("/")

def signup_hospital(request):
    if(user_data.getUserType(request.user.id) == "Hospital"):
        if(user_data.isVerifiedUser(request.user.id)):
            messages.info(request,"You're Details Have Already Been Submitted!")
            return redirect("/")
        else:
            data={'specialities':medical_speciality.get_specialities()}
            data['countries']=location.getCountries()
            return render(request,'accounts/signup_hospital.html',data)
    else:
        messages.info(request,"You Can't Access This Page!")
        return redirect("/")

def signup_tlab(request):
    if(user_data.getUserType(request.user.id) == "Testing Lab"):
        if(user_data.isVerifiedUser(request.user.id)):
            messages.info(request,"You're Details Have Already Been Submitted!")
            return redirect("/")
        else:
            data={'tests':medical_tests.list_of_medical_tests()}
            data['countries']=location.getCountries()
            return render(request,'accounts/signup_tlab.html',data)
    else:
        messages.info(request,"You Can't Access This Page!")
        return redirect("/")

def signup_patient(request):
    if(user_data.getUserType(request.user.id) == "Patient"):
        if(user_data.isVerifiedUser(request.user.id)):
            messages.info(request,"You're Details Have Already Been Submitted!")
            return redirect("/")
        else:
            data=dict()
            data['countries']=location.getCountries()
            return render(request,'accounts/signup_patient.html', data)
    else:
        messages.info(request,"You Can't Access This Page!")
        return redirect("/")

def login(request):
    email=request.POST['email']
    password=request.POST['password']

    #Validation checks
    if(len(email)>254):
        messages.info(request,"Invalid Email! Email can't have more than 254 characters.")
    elif(len(email)<8):
        messages.info(request,"Invalid Email! Email must contain atleast 8 characters")
    elif(len(password)<8):
        messages.info(request,"Invalid Password! Password must contain atleast 8 characters.")
    elif(len(password)>50):
        messages.info(request,"Invalid Password! Password can't have more than 50 characters.")
    else:
        if(authenticate.login(request, email, password)):
            messages.info(request,'Login Successful!')
            request.session['email']=email
            return redirect("/")
        else:
            messages.info(request,"Wrong Email or password!")
    return redirect("/accounts/signin")

def register(request):
    user_type=request.POST['user_type']
    name=request.POST['name']
    password=request.POST['password']
    password2=request.POST['password2']
    email=request.POST['email']


    #Validation checks
    if(len(user_type)==0):
        messages.info(request,"Please Select a Valid User Type!")
    if(len(name)==0):
        messages.info(request,"Invalid Name! Name can't be empty.")
    elif(len(name)>200):
        messages.info(request,"Invalid Name! Name can't have more than 200 characters.")
    elif(len(email)==0):
        messages.info(request,"Invalid Email! Email can't be empty.")
    elif(len(email)>254):
        messages.info(request,"Invalid Email! Email can't have more than 254 characters.")
    elif(len(password)<8):
        messages.info(request,"Invalid Password! Password can't have less than 8 characters.")
    elif(len(password)>50):
        messages.info(request,"Invalid Password! Password can't have more than 50 characters.")
    elif(password != password2):
        messages.info(request,"Invalid Password! Confirm Password and Password fields doesn't match.")
    
    else:
        if(authenticate.hasRegisteredEmail(email)):
            messages.info(request,'This Email is already registered!')
        # elif(authenticate.hasRegisteredPhone(phone)):
        #     messages.info(request,'This Phone is already registered!')
        else:
            if(authenticate.register(name, user_type, password, email)):
                messages.info(request,'Registeration Successful! You will recieve a verification mail for your account shortly.')
                return redirect("/")
            else:
                messages.info(request,"Registeration Failed!")
    return redirect("/accounts/signup")

def register_doctor(request):
    start_time=request.POST['start_time']
    end_time=request.POST['end_time']
    phone=request.POST['phone']
    is_independent=(request.POST['is_independent']=="True")
    gender=request.POST['gender']
    experience=int(request.POST['experience'])
    specialization=request.POST['specialization']

    proof=None
    if 'proof' in request.FILES:
        proof = request.FILES['proof']
    else:
        messages.info(request,'Please Upload Proof of Claimed Qualification.')
        return redirect("/accounts/signup/doctor")

    hospitalid=None
    cname=""
    cphoto=None
    fee=None
    country=""
    state=""
    city=""
    area=""
    zip=None

    if(is_independent):
        cname=request.POST['cname']
        if 'cphoto' in request.FILES:
            cphoto = request.FILES['cphoto']
        fee=int(request.POST['fee'])
        country=request.POST['country']
        state=request.POST['state']
        city=request.POST['city']
        area=request.POST['area']
        zip=int(request.POST['zip'])
    else:
        hospitalid=int(request.POST['hospitalid'])


    #Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    elif(authenticate.hasRegisteredPhone(phone, "Doctor")):
        messages.info(request,'This Phone is already registered!')
    else:
        phone=int(phone)
        if(request.user.is_authenticated):
            uid=request.user.id
            if(authenticate.registerDoctor(uid, start_time, end_time, phone, is_independent, gender, experience, specialization, proof, hospitalid, cname, cphoto, fee, country, state, city, area, zip)):
                messages.info(request,'Registeration Successful! Your account will be verified soon after review by our team.')
                return redirect("/")
            else:
                messages.info(request,"Registeration Failed!")
        else:
            messages.info(request,"Please Login Before Submitting Details.")
    return redirect("/accounts/signup/doctor")

def register_hospital(request):
    phone=request.POST['phone']
    country=request.POST['country']
    state=request.POST['state']
    city=request.POST['city']
    area=request.POST['area']
    zip=int(request.POST['zip'])
    pic1=None
    specialization=request.POST.getlist('specialization')
    certificate=None

    if 'proof' in request.FILES:
        certificate = request.FILES['proof']
    else:
        messages.info(request,'Please Upload A Valid Licsense Or Certification Of Hospital.')
        return redirect("/accounts/signup/hospital")

    if 'pic1' in request.FILES:
        pic1 = request.FILES['pic1']

    speciality_pricing=dict()
    for sp in specialization:
        speciality_pricing[sp]=request.POST[sp]

    # Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    elif(authenticate.hasRegisteredPhone(phone, "Hospital")):
        messages.info(request,'This Phone is already registered!')
    else:
        phone=int(phone)
        if(request.user.is_authenticated):
            uid=request.user.id
            if(authenticate.registerHospital(uid, phone, country, state, city, zip, area, speciality_pricing, pic1, certificate)):
                messages.info(request,'Registeration Successful! Your account will be verified soon after review by our team.')
                return redirect("/")
            else:
                messages.info(request,"Registeration Failed!")
        else:
            messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/accounts/signup/hospital")

def register_tlab(request):
    phone=request.POST['phone']
    country=request.POST['country']
    state=request.POST['state']
    city=request.POST['city']
    area=request.POST['area']
    zip=int(request.POST['zip'])
    pic1=None
    specialization=request.POST.getlist('specialization')
    certificate=None

    if 'proof' in request.FILES:
        certificate = request.FILES['proof']
    else:
        messages.info(request,'Please Upload A Valid Licsense Or Certification Of Hospital.')
        return redirect("/accounts/signup/hospital")

    if 'pic1' in request.FILES:
        pic1 = request.FILES['pic1']

    test_pricing=dict()
    for sp in specialization:
        test_pricing[sp]=request.POST[sp]

    # Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    elif(authenticate.hasRegisteredPhone(phone, "Hospital")):
        messages.info(request,'This Phone is already registered!')
    else:
        phone=int(phone)
        if(request.user.is_authenticated):
            uid=request.user.id
            if(authenticate.registerTLab(uid, phone, country, state, city, zip, area, test_pricing, pic1, certificate)):
                messages.info(request,'Registeration Successful! Your account will be verified soon after review by our team.')
                return redirect("/")
            else:
                messages.info(request,"Registeration Failed!")
        else:
            messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/accounts/signup/hospital")



def register_patient(request):
    phone=request.POST['phone']
    country=request.POST['country']
    state=request.POST['state']
    city=request.POST['city']
    area=request.POST['area']
    zip=int(request.POST['zip'])
    gender=request.POST['gender']
    age=int(request.POST['age'])
    disability=request.POST['disability']
    
    profilepic=None
    if 'profilepic' in request.FILES:
        profilepic = request.FILES['profilepic']

    #Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    elif(authenticate.hasRegisteredPhone(phone, "Patient")):
        messages.info(request,'This Phone is already registered!')
    else:
        phone=int(phone)
        if(request.user.is_authenticated):
            uid=request.user.id
            if(authenticate.registerPatient(uid, phone, country, state, city, area, zip, gender, age, disability, profilepic)):
                messages.info(request,'Registeration Successful! Your account is fully activated.')
                return redirect("/")
            else:
                messages.info(request,"Registeration Failed!")
        else:
            messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/accounts/signup/patient")

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and tokens.account_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.info(request,"Thanks for your email confirmation. You can login to your account now.")
        return redirect("/accounts/signin")
    else:
        messages.info(request,"Invalid Activation link!")
        return redirect("/accounts/signup")