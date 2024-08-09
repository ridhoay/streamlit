from django.db import models
from django.contrib.auth.models import User


class TodoItem(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)


class Club(models.Model):
    name = models.CharField(max_length=220)
    money = models.IntegerField()

    def __str__(self):
        return "{} - {}".format(self.name, self.money)


class PriceTrackerUser(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField('User Email')

    def __str__(self):
        return self.first_name


class ScrapedItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    items_sold = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    link = models.URLField(null=True)
    url = models.URLField(null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
