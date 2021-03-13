from django.urls import path
from . import views
urlpatterns = [
    path('profile/<int:uid>/', views.profile, name='profile'),
    path('unfollow/<int:uid>/', views.unfollow, name='unfollow'),
    path('follow/<int:uid>/', views.follow, name='follow'),
    path('rate/<int:uid>/<int:rating>', views.rate, name='rate'),
]