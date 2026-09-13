from django.urls import path
from .views import *

urlpatterns = [
    path('',index,name='index'),
    path('logout/', sair, name='logout'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    
]