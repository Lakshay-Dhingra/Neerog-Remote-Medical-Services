from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('Doctor/',views.Hospitals,name='Dashboard'),
    path('Doctor/states/',views.list_of_states,name='select'),
    path('Doctor/city/',views.list_of_city,name='city'),
    path('Doctor/Hospital',views.list_of_hospital,name="list_of_hospital"),
    path('profile/',views.profile,name='profile'),
    path('index/', views.index, name='index'),
    path('select_speciality/',views.select_speciality,name="select_speciality"),
    path('select_speciality/date/',views.chosen_date,name="chosen_date"),
    path('book_appointment1/<str:speciality>',views.book_appointment1,name="book_appointment1"),
    path('Appointment_Details_Submission/',views.Appointment_Details_Submission,name='Appointment_Details_Submission'),
    path('Selected/<str:hospital_id>/',views.Selected_Service_Provider,name="Selected"),
    path('prescription',views.Add_Prescription,name="prescription"),
    path('submit_Prescription',views.submit_Prescription,name="submit_Prescription"),
    path('book_appointment/',views.Book_Appointment,name="book_appointment"),
]