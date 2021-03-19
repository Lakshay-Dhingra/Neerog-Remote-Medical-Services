from django.shortcuts import render, redirect
from django.contrib import messages
from main_app import user_data, medical_speciality
import datetime


def profile(request, uid):
    if(user_data.isUser(uid)):
        user_type=user_data.getUserType(uid)
        if(user_data.isRegisteredUser(uid)):
            if(user_type == "Doctor"):
                doctor_data = user_data.getDoctorData(uid)
                try:
                    mydate=request.session['date']
                except:
                    mydate = datetime.datetime.now() + datetime.timedelta(days=1)
                doctor_data['AvailableSlots']=user_data.getFreeSlots(uid, mydate)
                doctor_data['SelectedDate']= datetime.datetime.strptime(mydate, '%Y-%m-%d')
                doctor_data['Today']= datetime.datetime.now()
                # print(mydate)
                # print(type(mydate))

                try:
                    mode = request.session['mode']
                except:
                    mode = "Online"
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
                messages.info(request,"You Are Not A Doctor!") #Temporary
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
                return render(request,'user_app/EditDoctorProfile.html',doctor_data)
            else:
                messages.info(request,"You Are Not A Doctor!") #Temporary
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
        return redirect("/user/profile/"+str(uid))
    else:
        #User not logged in
        messages.info(request,"You are not Logged In!")
        return redirect("/accounts/signin")

def follow(request, uid):
    if(request.user.is_authenticated):
        #User is logged in
        fid=request.user.id
        user_data.follow(uid, fid)
        return redirect("/user/profile/"+str(uid))
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
        return redirect("/user/profile/"+str(uid))
    else:
        #User not logged in
        messages.info(request,"You are not Logged In!")
        return redirect("/accounts/signin")

def setDate(request, uid):
    request.session['date'] = request.POST['date']
    return redirect("/user/profile/"+str(uid)+"#free_timing")

def setMode(request, uid):
    request.session['mode'] = request.POST['mode']
    return redirect("/user/profile/"+str(uid)+"#free_timing")