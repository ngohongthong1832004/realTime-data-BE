from django.urls import path
from .views import *


urlpatterns = [

    path('register/', Register.as_view(), name='user-registration'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    path('', Home.as_view(), name='home'),
]
    