from django.contrib.auth.models import User,auth
from main_app.models import UserDetails
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from . import tokens

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
        return False

def hasRegisteredEmail(email):
    try:
        UserDetails.objects.get(email=email)
        return True
    except:
        return False

def hasRegisteredPhone(phone):
    try:
        UserDetails.objects.get(phone=phone)
        return True
    except:
        return False