from django.db import models
from adm.models import *
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import date,time



class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    def clean(self):
        if self.age < 18 :
            raise ValueError("Age must be 18 or above")
    wallet_coins = models.FloatField(default=5000)

    def __str__(self):
        return self.user.username

class Tournament(models.Model):
    name = models.CharField(max_length=200)
    entry_fee = models.IntegerField()
    prize = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    max_player_count=models.IntegerField()

    def __str__(self):
        return self.name

class UserGameHistoriesRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input = models.CharField(max_length=200)
    output = models.CharField(max_length=255, blank=True)
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.input}"

class UserGameRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempt_count = models.IntegerField()
    max_score = models.IntegerField(null=True, blank=True)
    secret=models.CharField(max_length=4,blank=True)
    status = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

class UserTournamentLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tournament.name}"
