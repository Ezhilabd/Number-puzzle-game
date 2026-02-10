from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('',signin,name="home"),
   path('signup',signup,name='signup'),
    path('signin',signin,name='signin'),
    path('main',main,name='main'),
    path('leaderboard/',leaderboard_view, name='leaderboard'),
    path('tournament_history/',tournament_history_view, name='tournament_history'),
    path('new_tournament/',new_tournament_view, name='new_tournament'),
    path('play_tournament/<int:tournament_id>/',play_tournament, name='play_tournament'),
    path('play_game/',play_game, name='play_game'),
    path("restart_game/",restart_game,name='restart_game'),
    path('logout/',logout_view, name='logout'),
]