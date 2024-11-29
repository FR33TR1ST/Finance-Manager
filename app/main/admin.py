from django.contrib import admin
from .models import (Transaction, Account, Category, Type)
# Register your models here.
admin.site.register(Transaction)
admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Type)