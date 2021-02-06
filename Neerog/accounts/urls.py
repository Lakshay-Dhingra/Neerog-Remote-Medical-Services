from django.urls import path
from . import views
urlpatterns = [
    path('', views.signin, name='signin'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signup/doctor/', views.signup_doctor, name='signup_doctor'),
    path('signup/patient/', views.signup_patient, name='signup_patient'),
    path('signup/redirect/', views.signup_redirect, name='signup_redirect'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
]