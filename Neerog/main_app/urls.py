from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('Doctor/',views.doctor_dashboard,name='Dashboard'),
    path('Doctor/states/',views.list_of_states,name='select'),
    path('Doctor/city/',views.list_of_city,name='city'),
    path('Doctor/Hospital',views.list_of_hospital,name="list_of_hospital"),
    path('index/', views.index, name='index'),
    path('Profile/',views.profile,name='profile'),
    path('abc/',views.abc,name='abc'),
]