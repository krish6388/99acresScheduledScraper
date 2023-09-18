from django.db import models

# Create your models here.

class Tracker(models.Model):
    id = models.AutoField(primary_key=True)
    execution_time = models.DateTimeField()
    city = models.CharField(max_length=255)
    num_records = models.PositiveIntegerField()

class Property(models.Model):
    name = models.CharField(max_length=255)
    cost = models.CharField(max_length=255)
    type = models.CharField(max_length=20)
    area = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    link = models.URLField()

class PropertyBkp(models.Model):
    name = models.CharField(max_length=255)
    cost = models.CharField(max_length=255)
    type = models.CharField(max_length=20)
    area = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    link = models.URLField()

class PropertyTemp(models.Model):
    name = models.CharField(max_length=255)
    cost = models.CharField(max_length=255)
    type = models.CharField(max_length=20)
    area = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    link = models.URLField()