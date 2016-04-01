from __future__ import unicode_literals
from django.db import models


class CarsModel(models.Model):
    """docstring for CarsModel"""
    file_name = models.CharField(max_length=60)
    car_type = models.CharField(max_length=10)


class ProgressModel(models.Model):
    """docstring for ProgressModel"""
    file_name = models.CharField(max_length=60, primary_key=True)
    progress = models.IntegerField()

