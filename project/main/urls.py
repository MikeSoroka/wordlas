from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', LogoutView.as_view(next_page='register'), name='logout'),
]