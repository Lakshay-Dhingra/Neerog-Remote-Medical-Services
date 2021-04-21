from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    # path('home/', views.home, name='home'),
    path('Hospital_Selection/',views.Hospitals,name='Dashboard'),
    path('user_location/',views.user_location,name='user_location'),
    path('Hospital_Selection/states/',views.list_of_states,name='select'),
    path('availablity',views.availablity,name='availablity'),
    path('change_date',views.change_date,name='change_date'),
    path('Hospital_Selection/city/',views.list_of_city,name='city'),
    path('Hospital_Selection/Hospital',views.list_of_hospital,name="list_of_hospital"),
    path('dashboard/<int:id>',views.profile,name='dashboard'),
    path('report/',views.report,name='report'),
    path('verify_certificate/<str:id>',views.verify_certificate,name='verify_certificate'),
    path('index/', views.index, name='index'),
    path('select_speciality/<int:service_provider_id>',views.select_speciality,name="select_speciality"),
    path('select_speciality/date/',views.chosen_date,name="chosen_date"),
    path('Appointment_Details/<str:appointment_id>',views.Appointment_Details,name='Appointment_Details'),
    path('book_appointment1/<str:speciality>/<int:service_provider_id>',views.book_appointment1,name="book_appointment1"),
    path('Appointment_Details_Submission/',views.Appointment_Details_Submission,name='Appointment_Details_Submission'),
    path('Selected/<str:user_id>/',views.Selected_Service_Provider,name="Selected"),
    path('prescription',views.Add_Prescription,name="prescription"),
    path('submit_Prescription',views.submit_Prescription,name="submit_Prescription"),
    path('book_appointment/',views.Book_Appointment,name="book_appointment"),
    path('search_appointments',views.search_appointments,name='search_appointments'),
    path('admin_search_appointments',views.admin_search_appointments,name='admin_search_appointments'),
    #path('admin1',views.admin,name='admin1'),
    #path('Selected/<str:user_id>/', views.Selected_Service_Provider, name="Selected"),
    path('Appointment_Details_Submission1/', views.Appointment_Details_Submission1,
         name='Appointment_Details_Submission1'),
    path('Payment/',views.Payment,name="Payment"),
    path('cancel_appointment/',views.cancel_appointment,name="cancel_appointment"),
    path("add_news/<str:id>",views.add_news,name='add_news'),
    path("submit_news",views.submit_news,name="submit_news"),
    path("edit_time/<int:id>",views.edit_time,name="edit_time"),
    path("search/", views.search, name="search")
]
import main_app.jobs  # NOQA @isort:skip
import logging
logging.basicConfig(level="DEBUG")