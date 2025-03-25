from django.db import models
from django.conf import settings


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    name = models.CharField(max_length=100)
    type = models.ForeignKey('Type', on_delete=models.CASCADE)   # Debit, Credit, etc.
    account = models.ForeignKey('Account', on_delete=models.CASCADE)  # Checking, Savings, Credit Card, etc.
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)   # Food, Rent, etc.
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.CharField(max_length=256)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)     # Checking, Savings, Credit Card, etc.
    currency = models.CharField(max_length=3)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name},{self.currency}, {self.balance}"


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
