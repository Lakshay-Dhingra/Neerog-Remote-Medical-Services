from main_app.models import UserDetails, Doctor, Hospital, Patient, TestingLab, Follow, Ratings, Appointment_Timings, HospitalSpeciality, TestPricing
import sys, datetime
from accounts import authenticate
from django.core.files.storage import FileSystemStorage

def getUserType(uid):
    userobj=UserDetails.objects.get(userid=uid)
    return str(userobj.user_type)

#Users which are completely verified.
def isVerifiedUser(uid):
    user_type=getUserType(uid)
    if(user_type == "Doctor"):
        try:
            doctorobj=Doctor.objects.get(doctorid=uid)
            if(str(doctorobj.verified) == "No"):
                print(uid)
                return False
            else:
                print(uid)
                return True
        except:
            return False
    elif(user_type == "Hospital"):
        try:
            hospitalobj=Hospital.objects.get(hospitalid=uid)
            if(str(hospitalobj.verified) == "No"):
                return False
            else:
                return True
        except:
            return False
    elif(user_type == "Patient"):
        try:
            patientobj=Patient.objects.get(patientid=uid)
            return True
        except:
            return False

#Users which have submitted details but aren't verified yet.
def isRegisteredUser(uid):
    user_type=getUserType(uid)
    if(user_type == "Doctor"):
        try:
            Doctor.objects.get(doctorid=uid)
            return True
        except:
            return False
    elif(user_type == "Hospital"):
        try:
            Hospital.objects.get(hospitalid=uid)
            return True
        except:
            return False
    elif(user_type == "Patient"):
        try:
            Patient.objects.get(patientid=uid)
            return True
        except:
            return False
    elif(user_type == "Testing Lab"):
        try:
            TestingLab.objects.get(tlabid=uid)
            return True
        except:
            return False

def isUser(uid):
    try:
        UserDetails.objects.get(userid=uid)
        return True
    except:
        return False

def getDoctorData(uid):
    doctor_data = dict()
    userobj=UserDetails.objects.get(userid=uid)
    doctorobj=Doctor.objects.get(doctorid=uid)

    doctor_data['uid'] = uid
    doctor_data['Name'] = userobj.name
    doctor_data['Email'] = userobj.email
    doctor_data['DateJoined'] = userobj.created_at.date()
    doctor_data['AvgUserRating'] = userobj.avg_rating
    doctor_data['Followers'] = userobj.followers

    doctor_data['Phone'] = doctorobj.phone
    doctor_data['SpecializedIn'] = doctorobj.specialization
    doctor_data['Gender'] = doctorobj.gender
    doctor_data['About'] = doctorobj.about
    doctor_data['Experience'] = doctorobj.experience

    if doctorobj.profile_pic is None:
        doctor_data['ProfilePictureUrl'] = None
    elif doctorobj.profile_pic == "":
        doctor_data['ProfilePictureUrl'] = None
    else:
        doctor_data['ProfilePictureUrl'] = doctorobj.profile_pic.url
    doctor_data['Verified'] = doctorobj.verified

    doctor_data['independent']=doctorobj.is_independent

    if(doctor_data['independent']):
        doctor_data['WorksAt'] = doctorobj.clinic_name
        doctor_data['InstitutePhotoUrl'] = doctorobj.clinic_photo.url
        doctor_data['Country'] = doctorobj.country
        doctor_data['State'] = doctorobj.state
        doctor_data['City'] = doctorobj.city
        doctor_data['Area'] = doctorobj.area
        doctor_data['Zip'] = doctorobj.zip
        doctor_data['Fee'] = doctorobj.clinic_fee
    else:
        hospitalobj = doctorobj.hospitalid
        # print(type(hospitalobj))
        hospitaluserobj = hospitalobj.hospitalid
        # print(type(hospitaluserobj))
        hospitalid = hospitaluserobj.userid

        hospitalspeciality=None
        try:
            hospitalspeciality=HospitalSpeciality.objects.get(hospitalid=hospitalid, speciality = doctor_data['SpecializedIn'])
        except:
            pass

        doctor_data['WorksAt'] = hospitaluserobj.name
        doctor_data['InstitutePhotoUrl'] = hospitalobj.pic1.url
        doctor_data['Country'] = hospitalobj.country
        doctor_data['City'] = hospitalobj.city
        doctor_data['State'] = hospitalobj.state
        doctor_data['Area'] = hospitalobj.area
        doctor_data['Zip'] = hospitalobj.zip
        if hospitalspeciality is None:
            doctor_data['Fee']=None
        else:
            doctor_data['Fee'] = hospitalspeciality.price
    return doctor_data

# def getNumberOfFollowers(uid):
#     userobj=UserDetails.objects.get(userid=uid)
#     return userobj.followers

# def getAvgRating(uid):
#     userobj=UserDetails.objects.get(userid=uid)
#     return userobj.avg_rating

def isFollowing(influencer, follower):
    try:
        Follow.objects.get(influencerid=influencer, followerid=follower)
        return True
    except:
        return False

def userRating(influencer, rater):
    try:
        ratingobj = Ratings.objects.get(influencerid=influencer, raterid=rater)
        return ratingobj.rating
    except:
        return 0

def unfollow(influencer, follower):
    try:
        fobj = Follow.objects.get(influencerid=influencer, followerid=follower)
        fobj.delete()
        iobj=UserDetails.objects.get(userid=influencer)
        iobj.followers -=1
        iobj.save()
    except:
        print(sys.exc_info())

def follow(influencer, follower):
    try:
        Follow.objects.get(influencerid=influencer, followerid=follower)
        #if already following
    except:
        iobj=UserDetails.objects.get(userid=influencer)
        fobj=UserDetails.objects.get(userid=follower)
        follow=Follow(influencerid=iobj,followerid=fobj)
        follow.save()
        iobj.followers +=1
        iobj.save()

def rate(influencer, rater, rating):
    try:
        #if already rated
        ratingobj = Ratings.objects.get(influencerid = influencer, raterid = rater)
        ratingobj.rating = rating
        ratingobj.save()
    except:
        #if rating first time
        sys.exc_info()
        iobj=UserDetails.objects.get(userid=influencer)
        robj=UserDetails.objects.get(userid=rater)
        ratingobj = Ratings(influencerid=iobj,raterid=robj, rating = rating)
        ratingobj.save()

def getFreeSlots(uid, mydate):
    slots = []
    service_provider=UserDetails.objects.get(userid=uid)
    t = Appointment_Timings.objects.filter(service_provider_id=uid).filter(date=mydate)
    if len(t) > 0:
        if (t[0].available == False):
            # messages.info(request, "Doctor not availaible on this date")
            return None
        else:
            for i in t:
                if (i.Booked==False):
                    t12=i.time.split(":")
                    d12=str(i.date).split("-")
                    #print(d12)
                    da=datetime.datetime(int(d12[0]),int(d12[1]),int(d12[2]),int(t12[0]),int(t12[1]),int(t12[2]))
                    slots.append(da)
            if(len(slots)==0):
                # messages.info(request, "Doctor not availaible on this date")
                return None
    else:
        p13 = UserDetails.objects.get(userid=uid)
        print(p13.user_type)
        if (p13.user_type == "Doctor"):
            d1 = Doctor.objects.get(doctorid=service_provider)
            start_time = d1.start_time.split(":")
            end_time = d1.end_time.split(":")
            print(start_time, end_time)
        else:
                    """t1 = TestingLab.objects.get(tlabid=service_provider)
                    start_time = t1.start_time.split(":")
                    end_time = t1.end_time.split(":")
                    print(start_time, end_time)"""
                    start_time = [9, 0, 0]
                    end_time = [16, 0, 0]


        date = mydate.split("-")
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

def getHospitalId(uid):
    doctorobj=Doctor.objects.get(doctorid=uid)
    return doctorobj.hospitalid

def editPatient(request, uid, name, phone, gender, age, blood, about, country, state, city, area, zip, disability):
    success=True
    userobj=UserDetails.objects.get(userid=uid)
    userobj.name = name
    userobj.save()

    pobj=Patient.objects.get(patientid=uid)

    if(pobj.phone != phone):
        if(authenticate.hasRegisteredPhone(phone, "Patient")):
            success=False
        else:
            pobj.phone=phone
    
    pobj.age = age
    pobj.gender = gender
    pobj.blood_group = blood
    pobj.disability = disability
    pobj.about = about
    
    pobj.country = country
    pobj.state = state
    pobj.city = city
    pobj.area = area
    pobj.zip = zip

    if 'profilepic' in request.FILES:
        pobj.profile_pic=request.FILES['profilepic']

    pobj.save()
    return success


def editDoctor(request, uid, name, phone, gender, experience, is_independent, specialization, about, hospitalid, country, city, area, cname, fee):
    success=True
    userobj=UserDetails.objects.get(userid=uid)
    userobj.name = name
    userobj.save()

    doctorobj=Doctor.objects.get(doctorid=uid)

    if(doctorobj.phone != phone):
        if(authenticate.hasRegisteredPhone(phone, "Doctor")):
            success=False
        else:
            doctorobj.phone=phone
    
    doctorobj.gender = gender
    doctorobj.experience = experience
    doctorobj.is_independent = is_independent
    doctorobj.specialization = specialization
    doctorobj.about = about

    if hospitalid is not None:
        doctorobj.hospitalid = Hospital.objects.get(hospitalid = hospitalid)
    
    doctorobj.country = country
    doctorobj.city = city
    doctorobj.area = area
    doctorobj.clinic_name = cname
    doctorobj.clinic_fee =fee


    if 'profilepic' in request.FILES:
        doctorobj.profile_pic=request.FILES['profilepic']

    if 'cphoto' in request.FILES:
        doctorobj.clinic_photo=request.FILES['cphoto']

    doctorobj.save()
    return success

def editHospital(request, uid, name, phone, year, about, country, state, city, area, zip):
    success=True
    userobj=UserDetails.objects.get(userid=uid)
    userobj.name = name
    userobj.save()

    hobj=Hospital.objects.get(hospitalid=uid)

    if(hobj.phone != phone):
        if(authenticate.hasRegisteredPhone(phone, "Hospital")):
            success=False
        else:
            hobj.phone=phone
    
    hobj.year_established = year
    hobj.about = about
    
    hobj.country = country
    hobj.state = state
    hobj.city = city
    hobj.area = area
    hobj.zip = zip

    if 'pic1' in request.FILES:
        hobj.pic1=request.FILES['pic1']

    if 'pic2' in request.FILES:
        hobj.pic2=request.FILES['pic2']

    if 'pic3' in request.FILES:
        hobj.pic3=request.FILES['pic3']

    if 'logo' in request.FILES:
        hobj.hospital_logo=request.FILES['logo']

    hobj.save()
    return success

def editHospitalSpeciality(uid, speciality_pricing):
    hsobjs = HospitalSpeciality.objects.filter(hospitalid = uid)
    if hsobjs is not None:
        hsobjs.delete()
    try:
        hobj=Hospital.objects.get(hospitalid=uid)
        for sp in speciality_pricing:
            hospitalspeciality = HospitalSpeciality(hospitalid=hobj, speciality = sp, price=speciality_pricing[sp])
            hospitalspeciality.save()
    except:
        print(sys.exc_info())


def editTLab(request, uid, name, phone, year, about, country, state, city, area, zip):
    success=True
    userobj=UserDetails.objects.get(userid=uid)
    userobj.name = name
    userobj.save()

    tobj=TestingLab.objects.get(tlabid=uid)

    if(tobj.phone != phone):
        if(authenticate.hasRegisteredPhone(phone, "Testing Lab")):
            success=False
        else:
            tobj.phone=phone
    
    tobj.year_established = year
    tobj.about = about
    
    tobj.country = country
    tobj.state = state
    tobj.city = city
    tobj.area = area
    tobj.zip = zip

    if 'pic1' in request.FILES:
        tobj.lab_photo=request.FILES['pic1']

    if 'logo' in request.FILES:
        tobj.tlab_logo=request.FILES['logo']

    tobj.save()
    return success

def editTestPricing(uid, speciality_pricing):
    tpobjs = TestPricing.objects.filter(tlabid = uid)
    if tpobjs is not None:
        tpobjs.delete()
    try:
        tobj=TestingLab.objects.get(tlabid=uid)
        for sp in speciality_pricing:
            testpricing = TestPricing(tlabid=tobj, testname = sp, price=speciality_pricing[sp])
            testpricing.save()
    except:
        print(sys.exc_info())

def getHospitalData(uid):
    hp_data = dict()
    userobj=UserDetails.objects.get(userid=uid)
    hpobj=Hospital.objects.get(hospitalid=uid)

    hp_data['uid'] = uid
    hp_data['Name'] = userobj.name

    hp_data['Phone'] = hpobj.phone
    hp_data['About'] = hpobj.about
    hp_data['YearEstablished'] = hpobj.year_established

    if hpobj.hospital_logo is None:
        hp_data['Logo'] = None    
    elif hpobj.hospital_logo == "":
        hp_data['Logo'] = None
    else:
        hp_data['Logo'] = hpobj.hospital_logo.url
    if hpobj.pic2 is None:
        hp_data['Pic2'] = None    
    elif hpobj.pic2 == "":
        hp_data['Pic2'] = None
    else:
        hp_data['Pic2'] = hpobj.pic2.url

    if hpobj.pic3 is None:
        hp_data['Pic3'] = None    
    elif hpobj.pic3 == "":
        hp_data['Pic3'] = None
    else:
        hp_data['Pic3'] = hpobj.pic3.url

    hp_data['Verified'] = hpobj.verified

    hp_data['Pic1'] = hpobj.pic1.url
    hp_data['Country'] = hpobj.country
    hp_data['State'] = hpobj.state
    hp_data['City'] = hpobj.city
    hp_data['Area'] = hpobj.area
    hp_data['Zip'] = hpobj.zip

    speciality_fee = dict()
    hspobjs = HospitalSpeciality.objects.filter(hospitalid = hpobj)
    for obj in hspobjs:
        speciality_fee[obj.speciality] = obj.price
    
    hp_data['SpecialityFee'] = speciality_fee
    
    return hp_data

def getTestingLabData(uid):
    tl_data = dict()
    userobj=UserDetails.objects.get(userid=uid)
    tobj=TestingLab.objects.get(tlabid=uid)

    tl_data['uid'] = uid
    tl_data['Name'] = userobj.name

    tl_data['Phone'] = tobj.phone
    tl_data['About'] = tobj.about
    tl_data['YearEstablished'] = tobj.year_established

    if tobj.tlab_logo is None:
        tl_data['Logo'] = None    
    elif tobj.tlab_logo == "":
        tl_data['Logo'] = None
    else:
        tl_data['Logo'] = tobj.tlab_logo.url

    tl_data['Verified'] = tobj.verified

    tl_data['Pic1'] = tobj.lab_photo.url
    tl_data['Country'] = tobj.country
    tl_data['State'] = tobj.state
    tl_data['City'] = tobj.city
    tl_data['Area'] = tobj.area
    tl_data['Zip'] = tobj.zip

    speciality_fee = dict()
    tpobjs = TestPricing.objects.filter(tlabid = tobj)
    for obj in tpobjs:
        speciality_fee[obj.testname] = obj.price
    
    tl_data['TestPrice'] = speciality_fee
    
    return tl_data
        
def getPatientData(uid):
    pt_data = dict()
    userobj=UserDetails.objects.get(userid=uid)
    pobj=Patient.objects.get(patientid=uid)

    pt_data['uid'] = uid
    pt_data['Name'] = userobj.name

    pt_data['Phone'] = pobj.phone
    pt_data['About'] = pobj.about
    pt_data['Gender'] = pobj.gender
    pt_data['Age'] = pobj.age
    pt_data['Blood'] = pobj.blood_group
    pt_data['Disability'] = pobj.disability

    if pobj.profile_pic is None:
        pt_data['ProfilePic'] = None    
    elif pobj.profile_pic == "":
        pt_data['ProfilePic'] = None
    else:
        pt_data['ProfilePic'] = pobj.profile_pic.url

    pt_data['Country'] = pobj.country
    pt_data['State'] = pobj.state
    pt_data['City'] = pobj.city
    pt_data['Area'] = pobj.area
    pt_data['Zip'] = pobj.zip
    
    return pt_data