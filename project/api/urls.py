from django.urls import path
from . import views

urlpatterns = [
    path('api/game/', views.handle_game_operations, name='handle_game_operations'),
    path('api/statistics/', views.get_statistics, name='get_statistics'),
]