from main_app.models import UserDetails, Doctor, Hospital, Patient, TestingLab, Follow, Ratings, Appointment_Timings, HospitalSpeciality
import sys, datetime
from accounts import authenticate
from django.core.files.storage import FileSystemStorage

def getUserType(uid):
    userobj=UserDetails.objects.get(userid=uid-1)
    return str(userobj.user_type)

#Users which are completely verified.
def isVerifiedUser(uid):
    user_type=getUserType(uid)
    if(user_type == "Doctor"):
        try:
            doctorobj=Doctor.objects.get(doctorid=uid-1)
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

#Users which have submitted details but aren't verified yet.
def isRegisteredUser(uid):
    user_type=getUserType(uid)
    if(user_type == "Doctor"):
        try:
            Doctor.objects.get(doctorid=uid-1)
            return True
        except:
            return False
    elif(user_type == "Hospital"):
        try:
            Hospital.objects.get(hospitalid=uid-1)
            return True
        except:
            return False
    elif(user_type == "Patient"):
        try:
            Patient.objects.get(patientid=uid-1)
            return True
        except:
            return False
    elif(user_type == "Testing Lab"):
        try:
            TestingLab.objects.get(tlabid=uid-1)
            return True
        except:
            return False

def isUser(uid):
    try:
        UserDetails.objects.get(userid=uid-1)
        return True
    except:
        return False

def getDoctorData(uid):
    doctor_data = dict()
    userobj=UserDetails.objects.get(userid=uid-1)
    doctorobj=Doctor.objects.get(doctorid=uid-1)

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
    doctor_data['ProfilePictureUrl'] = doctorobj.profile_pic.url
    doctor_data['Verified'] = doctorobj.verified

    doctor_data['independent']=doctorobj.is_independent

    if(doctor_data['independent']):
        doctor_data['WorksAt'] = doctorobj.clinic_name
        doctor_data['InstitutePhotoUrl'] = doctorobj.clinic_photo.url
        doctor_data['Country'] = doctorobj.country
        doctor_data['City'] = doctorobj.city
        doctor_data['Area'] = doctorobj.area
        doctor_data['Fee'] = doctorobj.clinic_fee
    else:
        hospitalobj = doctorobj.hospitalid
        # print(type(hospitalobj))
        hospitaluserobj = hospitalobj.hospitalid
        # print(type(hospitaluserobj))
        hospitalid = hospitaluserobj.userid
        hospitalspeciality=HospitalSpeciality.objects.get(hospitalid=hospitalid, speciality = doctor_data['SpecializedIn'])

        doctor_data['WorksAt'] = hospitaluserobj.name
        doctor_data['InstitutePhotoUrl'] = hospitalobj.pic1.url
        doctor_data['Country'] = hospitalobj.country
        doctor_data['City'] = hospitalobj.city
        doctor_data['Area'] = hospitalobj.area
        doctor_data['Fee'] = hospitalspeciality.price
    return doctor_data

# def getNumberOfFollowers(uid):
#     userobj=UserDetails.objects.get(userid=uid-1)
#     return userobj.followers

# def getAvgRating(uid):
#     userobj=UserDetails.objects.get(userid=uid-1)
#     return userobj.avg_rating

def isFollowing(influencer, follower):
    try:
        Follow.objects.get(influencerid=influencer-1, followerid=follower-1)
        return True
    except:
        return False

def userRating(influencer, rater):
    try:
        ratingobj = Ratings.objects.get(influencerid=influencer-1, raterid=rater-1)
        return ratingobj.rating
    except:
        return 0

def unfollow(influencer, follower):
    try:
        fobj = Follow.objects.get(influencerid=influencer-1, followerid=follower-1)
        fobj.delete()
        iobj=UserDetails.objects.get(userid=influencer-1)
        iobj.followers -=1
        iobj.save()
    except:
        print(sys.exc_info())

def follow(influencer, follower):
    try:
        Follow.objects.get(influencerid=influencer-1, followerid=follower-1)
        #if already following
    except:
        iobj=UserDetails.objects.get(userid=influencer-1)
        fobj=UserDetails.objects.get(userid=follower-1)
        follow=Follow(influencerid=iobj,followerid=fobj)
        follow.save()
        iobj.followers +=1
        iobj.save()

def rate(influencer, rater, rating):
    try:
        #if already rated
        ratingobj = Ratings.objects.get(influencerid = influencer-1, raterid = rater-1)
        ratingobj.rating = rating
        ratingobj.save()
    except:
        #if rating first time
        sys.exc_info()
        iobj=UserDetails.objects.get(userid=influencer-1)
        robj=UserDetails.objects.get(userid=rater-1)
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
                    print(d12)
                    da=datetime.datetime(int(d12[0]),int(d12[1]),int(d12[2]),int(t12[0]),int(t12[1]),int(t12[2]))
                    slots.append(da)
            if(len(slots)==0):
                # messages.info(request, "Doctor not availaible on this date")
                return None
    else:
        start_time = [9, 0, 0]
        end_time = [18, 0, 0]
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
    doctorobj=Doctor.objects.get(doctorid=uid-1)
    return doctorobj.hospitalid

def editDoctor(request, uid, name, phone, gender, experience, is_independent, specialization, about, hospitalid, country, city, area, cname, fee):
    success=True
    userobj=UserDetails.objects.get(userid=uid-1)
    userobj.name = name
    userobj.save()

    doctorobj=Doctor.objects.get(doctorid=uid-1)

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

    # doctor=Doctor(doctorid=userobj, phone=phone, about=about, is_independent=is_independent, gender=gender, experience=experience, specialization=specialization, profile_pic = profilepic, city= city, country= country, area=area, certificate=proof, clinic_name=cname, verified=verified, clinic_photo=cphoto, clinic_fee =fee, hospitalid = hospitalid)
    # doctor.save()

    return success
    
        