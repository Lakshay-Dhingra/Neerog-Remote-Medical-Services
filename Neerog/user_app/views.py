from django.shortcuts import render, redirect
from django.contrib import messages
from main_app import user_data


def profile(request, uid):
    if(user_data.isUser(uid)):
        user_type=user_data.getUserType(uid)
        if(user_data.isRegisteredUser(uid)):
            if(user_type == "Doctor"):
                doctor_data = user_data.getDoctorData(uid)
                if(request.user.is_authenticated):
                    #User is logged in
                    fid=request.user.id
                    doctor_data['Following']=user_data.isFollowing(uid, fid)
                    doctor_data['MyRating']=user_data.userRating(uid, fid)
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