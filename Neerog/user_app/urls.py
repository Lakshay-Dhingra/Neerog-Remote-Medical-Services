from django.urls import path
from . import views
urlpatterns = [
    path('profile/<int:uid>/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit/doctor/', views.edit_doctor, name='edit_doctor'),
    path('unfollow/<int:uid>/', views.unfollow, name='unfollow'),
    path('setDate/<int:uid>/', views.setDate, name='setDate'),
    path('setMode/<int:uid>/', views.setMode, name='setMode'),
    path('follow/<int:uid>/', views.follow, name='follow'),
    path('rate/<int:uid>/<int:rating>', views.rate, name='rate'),
]