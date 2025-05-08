from django.urls import path, include
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
]