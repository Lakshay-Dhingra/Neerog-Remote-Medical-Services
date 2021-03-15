
from django.contrib import admin
from .models import *

class UserDetailsAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('userid','user_type','name','email','created_at')
    #columns that have  a filter-by option
    list_filter=['user_type','created_at']

admin.site.register(UserDetails,UserDetailsAdmin)

class PatientAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('patientid','city','country','age','gender')
    #columns that have  a filter-by option
    list_filter=['city','country','age','gender','blood_group']

admin.site.register(Patient,PatientAdmin)

class HospitalAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('hospitalid','city','country','year_established','verified')
    #columns that have  a filter-by option
    list_filter=['city','country','year_established','verified']

admin.site.register(Hospital,HospitalAdmin)

class HospitalSpecialityAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('hospitalid','speciality','price')
    #columns that have  a filter-by option
    list_filter=['speciality','price']
class AppointmentslotsAdmin(admin.ModelAdmin):
    list_display = ('doctorid','available','date',"TestingLab")

admin.site.register(Appointment_slots,AppointmentslotsAdmin)

class AppointmentsAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('appointmentid','doctoremail','patientemail')
admin.site.register(HospitalSpeciality,HospitalSpecialityAdmin)

admin.site.register(Appointments,AppointmentsAdmin)
class DoctorAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('doctorid','city','country','gender','experience','verified')
    #columns that have  a filter-by option
    list_filter=['city','country','gender','experience','verified','is_independent']

admin.site.register(Doctor,DoctorAdmin)

class TestingLabAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('tlabid','city','country','year_established','verified')
    #columns that have  a filter-by option
    list_filter=['city','country','year_established','verified']

admin.site.register(TestingLab,TestingLabAdmin)

class TestPricingAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('tlabid','testname','price')
    #columns that have  a filter-by option
    list_filter=['testname','price']

admin.site.register(TestPricing,TestPricingAdmin)

class FollowAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('influencerid','followerid')
    #columns that have  a filter-by option
    list_filter=['influencerid','followerid']

admin.site.register(Follow,FollowAdmin)

class RatingsAdmin(admin.ModelAdmin):
    #columns which will be displayed in outer view
    list_display = ('influencerid','raterid', 'rating')
    #columns that have  a filter-by option
    list_filter=['influencerid','raterid', 'rating']

admin.site.register(Ratings,RatingsAdmin)