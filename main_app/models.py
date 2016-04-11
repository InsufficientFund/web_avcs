from __future__ import unicode_literals
from django.db import models
from datetime import datetime


class CarsModel(models.Model):
    """docstring for CarsModel"""
    file_name = models.CharField(max_length=60)
    car_type = models.CharField(max_length=10)
    frame = models.IntegerField()


class ProgressModel(models.Model):
    """docstring for ProgressModel"""
    file_name = models.CharField(max_length=60, primary_key=True)
    progress = models.IntegerField()
    max_frame = models.IntegerField()


class ResultModel(models.Model):
    """docstring for ProgressModel"""
    unique_name = models.CharField(max_length=60, primary_key=True)
    file_name = models.CharField(max_length=60)
    email = models.CharField(max_length=60)
    time = models.DateTimeField(default=datetime.now, blank=True)


class StateModel(models.Model):
    """docstring for StateModel"""
    state_name = models.CharField(max_length=60, primary_key=True)
    status = models.BooleanField()
