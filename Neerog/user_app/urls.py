from django.urls import path
from . import views
urlpatterns = [
    path('profile/<int:uid>/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit/doctor/', views.edit_doctor, name='edit_doctor'),
    path('profile/edit/hospital/', views.edit_hospital, name='edit_hospital'),
    path('profile/edit/hospital_speciality/', views.edit_hospital_speciality, name='edit_hospital_speciality'),
    path('profile/edit/testinglab/', views.edit_testinglab, name='edit_testinglab'),
    path('profile/edit/testpricing/', views.edit_testpricing, name='edit_testpricing'),
    path('unfollow/<int:uid>/', views.unfollow, name='unfollow'),
    path('setDate/<int:uid>/', views.setDate, name='setDate'),
    path('setMode/<int:uid>/', views.setMode, name='setMode'),
    path('follow/<int:uid>/', views.follow, name='follow'),
    path('rate/<int:uid>/<int:rating>', views.rate, name='rate'),
]