from django.shortcuts import render, redirect
from django.contrib import messages
from main_app import user_data, medical_speciality, location, medical_tests
import datetime


def profile(request, uid):
    uid= int(uid)+1
    if(user_data.isUser(uid)):
        user_type=user_data.getUserType(uid)
        if(user_data.isRegisteredUser(uid)):
            if(user_type == "Patient"):
                return redirect("/Selected/"+str(uid-1))
            elif(user_type == "Doctor"):
                doctor_data = user_data.getDoctorData(uid)
                try:
                    mydate=request.session['date']
                    # print(mydate)
                    mydate=datetime.datetime.strptime(mydate, '%Y-%m-%d')
                    # print(str(mydate).split()[0])
                except:
                    mydate = datetime.datetime.now() + datetime.timedelta(days=1)
                    request.session['date']=str(mydate.date())
                    print("fvv",request.session['date'])
                doctor_data['AvailableSlots']=user_data.getFreeSlots(uid, str(mydate).split()[0])
                doctor_data['SelectedDate']= mydate
                doctor_data['Today']= datetime.datetime.now()
                try:
                    mode = request.session['mode']
                except:
                    mode = "Online"
                    request.session['mode']="Online"
                doctor_data['SelectedMode'] = mode
                if(request.user.is_authenticated):
                    #User is logged in
                    fid=request.user.id
                    doctor_data['Following']=user_data.isFollowing(uid, fid)
                    doctor_data['MyRating']=user_data.userRating(uid, fid)
                    if(uid == fid):
                        doctor_data["Myself"]=True
                    else:
                        doctor_data["Myself"]=False
                else:
                    #User not logged in
                    doctor_data['Following']=False
                    doctor_data['MyRating']=0

                return render(request,'user_app/DoctorProfile.html',doctor_data)
            else:
                return redirect("/Selected/"+str(uid-1))
        else:
            messages.info(request,"This User Hasn't Completed Registeration yet!")
    else:
        messages.info(request,"Sorry, No Such User Exists!")
    return redirect("/")

def edit_profile(request):
    if(request.user.is_authenticated):
        #User is logged in
        uid=request.user.id
        user_type=user_data.getUserType(uid)
        if(user_data.isRegisteredUser(uid)):
            if(user_type == "Doctor"):
                doctor_data = user_data.getDoctorData(uid)
                
                doctor_data['AllSpecialities']=medical_speciality.get_specialities()
                doctor_data['AllGenders']=['Male', 'Female', 'Trans', 'Unknown']
                if(doctor_data["independent"]):
                    doctor_data['HospitalId']=""
                else:
                    doctor_data['HospitalId']=user_data.getHospitalId(uid)
                return render(request,'user_app/EditDoctorProfile.html',doctor_data)
            elif(user_type == "Hospital"):
                hp_data = user_data.getHospitalData(uid)
                hp_data['AllSpecialities']=medical_speciality.get_specialities()
                hp_data['Countries'] = location.getCountries()
                hp_data['States'] = location.get_states(hp_data['Country'])
                hp_data['Cities'] = location.list_of_cities1(hp_data['State'])
                return render(request,'user_app/EditHospitalProfile.html',hp_data)
            elif(user_type == "Testing Lab"):
                tl_data = user_data.getTestingLabData(uid)
                tl_data['tests']=medical_tests.getTests()
                tl_data['Countries'] = location.getCountries()
                tl_data['States'] = location.get_states(tl_data['Country'])
                tl_data['Cities'] = location.list_of_cities1(tl_data['State'])
                return render(request,'user_app/EditTLabProfile.html',tl_data)
            elif(user_type == "Patient"):
                pt_data = user_data.getPatientData(uid)
                pt_data['AllGenders'] = ['Male', 'Female', 'Trans', 'Unknown']
                pt_data['AllBG'] = ['A+ve', 'A-ve', 'B+ve', 'B-ve', 'AB+ve', 'AB-ve', 'O+ve', 'O-ve', 'HH+ve', 'HH-ve', 'Unknown']
                pt_data['Countries'] = location.getCountries()
                pt_data['States'] = location.get_states(pt_data['Country'])
                pt_data['Cities'] = location.list_of_cities1(pt_data['State'])
                return render(request,'user_app/EditPatientProfile.html',pt_data)
        else:
            messages.info(request,"You Haven't Completed Registeration yet!")
    else:
        #User not logged in
        messages.info(request,"You are not Logged In!")
        return redirect("/accounts/signin")

def unfollow(request, uid):
    if(request.user.is_authenticated):
        #User is logged in
        fid=request.user.id
        user_data.unfollow(uid, fid)
        messages.info(request,"Unfollowed Successfully!")
        return redirect("/user/profile/"+str(uid-1))
    else:
        #User not logged in
        messages.info(request,"You are not Logged In!")
        return redirect("/accounts/signin")

def follow(request, uid):
    if(request.user.is_authenticated):
        #User is logged in
        fid=request.user.id
        user_data.follow(uid, fid)
        return redirect("/user/profile/"+str(uid-1))
    else:
        #User not logged in
        messages.info(request,"You are not Logged In!")
        return redirect("/accounts/signin")

def rate(request, uid, rating):
    if(request.user.is_authenticated):
        #User is logged in
        rid=request.user.id
        user_data.rate(uid, rid, rating)
        messages.info(request,"Your Rating Updated!")
        return redirect("/user/profile/"+str(uid-1))
    else:
        #User not logged in
        messages.info(request,"You are not Logged In!")
        return redirect("/accounts/signin")

def setDate(request, uid):
    request.session['date'] = request.POST['date']
    return redirect("/user/profile/"+str(uid-1)+"#free_timing")

def setMode(request, uid):
    request.session['mode'] = request.POST['mode']
    return redirect("/user/profile/"+str(uid-1)+"#free_timing")

def edit_patient(request):
    name=request.POST['name']
    phone=request.POST['phone']
    gender=request.POST['gender']
    age=int(request.POST['age'])
    blood=request.POST['blood']
    country=request.POST['country']
    state=request.POST['state']
    city=request.POST['city']
    area=request.POST['area']
    zip=int(request.POST['zip'])
    about=request.POST['about']

    # about=""
    # if request.POST['about'] is None:
    #     pass
    # elif request.POST['about'] == '':
    #     pass
    # else:
    #     about=request.POST['about']

    disability=request.POST['disability']
        

    #Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    else:
        phone = int(phone)
        if(request.user.is_authenticated):
            uid=request.user.id
            if(user_data.editPatient(request, uid, name, phone, gender, age, blood, about, country, state, city, area, zip, disability)):
                messages.info(request,'Profile Updated Successfully!')
                return redirect("/user/profile/edit/")
            else:
                messages.info(request,"This Phone Number is already registered so Phone can't be updated!")
        else:
            messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/user/profile/edit/")


def edit_doctor(request):
    name=request.POST['name']
    phone=request.POST['phone']
    gender=request.POST['gender']
    experience=request.POST['experience']

    is_independent=request.POST['is_independent']
    if(is_independent == "True"):
        is_independent = True
    else:
        is_independent =False

    specialization=request.POST['specialization']
    about=request.POST['about']

    if(is_independent):
        country=request.POST['country']
        city=request.POST['city']
        area=request.POST['area']
        cname=request.POST['cname']
        fee=int(request.POST['fee'])
        hospitalid=None
    else:
        hospitalid=int(request.POST['hospitalid'])
        country=""
        city=""
        area=""
        cname=""
        fee=None

    #Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    else:
        if(request.user.is_authenticated):
            uid=request.user.id
            if(user_data.editDoctor(request, uid, name, int(phone), gender, int(experience), is_independent, specialization, about, hospitalid, country, city, area, cname, fee)):
                messages.info(request,'Profile Updated Successfully!')
                return redirect("/user/profile/edit/")
            else:
                messages.info(request,"This Phone Number is already registered so Phone can't be updated!")
        else:
            messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/user/profile/edit/")

def edit_hospital(request):
    name = request.POST['name']
    year = None
    phone=request.POST['phone']
    country=request.POST['country']
    state=request.POST['state']
    city=request.POST['city']
    area=request.POST['area']
    zip=int(request.POST['zip'])
    about= request.POST['about']

    if request.POST['year'] is None:
        pass
    elif request.POST['year'] == '':
        pass
    else:
        year=int(request.POST['year'])

    # Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    else:
        if(request.user.is_authenticated):
            uid=request.user.id
            if(user_data.editHospital(request, uid, name, int(phone), year, about, country, state, city, area, zip)):
                messages.info(request,'Profile Updated Successfully!')
                return redirect("/user/profile/edit/")
            else:
                messages.info(request,"This Phone Number is already registered so Phone can't be updated!")
        else:
            messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/user/profile/edit/")

def edit_hospital_speciality(request):
    specialization=request.POST.getlist('specialization')
    speciality_pricing=dict()
    
    for sp in specialization:
        speciality_pricing[sp]=request.POST[sp]

    if(request.user.is_authenticated):
        uid=request.user.id
        user_data.editHospitalSpeciality(uid, speciality_pricing)
        messages.info(request,'Profile Updated Successfully!')
        return redirect("/user/profile/edit/")
    else:
        messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/user/profile/edit/")

def edit_testinglab(request):
    name = request.POST['name']
    year = None
    phone=request.POST['phone']
    country=request.POST['country']
    state=request.POST['state']
    city=request.POST['city']
    area=request.POST['area']
    zip=int(request.POST['zip'])
    about= request.POST['about']

    if request.POST['year'] is None:
        pass
    elif request.POST['year'] == '':
        pass
    else:
        year=int(request.POST['year'])

    # Validation checks
    if(len(phone)==0):
        messages.info(request,"Invalid Phone Number! Phone Number can't be empty.")
    elif(len(phone)>10):
        messages.info(request,"Invalid Phone Number! Phone Number can't have more than 10 characters.")
    else:
        if(request.user.is_authenticated):
            uid=request.user.id
            if(user_data.editTLab(request, uid, name, int(phone), year, about, country, state, city, area, zip)):
                messages.info(request,'Profile Updated Successfully!')
                return redirect("/user/profile/edit/")
            else:
                messages.info(request,"This Phone Number is already registered so Phone can't be updated!")
        else:
            messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/user/profile/edit/")

def edit_testpricing(request):
    specialization=request.POST.getlist('specialization')
    speciality_pricing=dict()
    
    for sp in specialization:
        speciality_pricing[sp]=request.POST[sp]

    if(request.user.is_authenticated):
        uid=request.user.id
        user_data.editTestPricing(uid, speciality_pricing)
        messages.info(request,'Profile Updated Successfully!')
        return redirect("/user/profile/edit/")
    else:
        messages.info(request,"Please Login Before Submitting Details!")
    return redirect("/user/profile/edit/")