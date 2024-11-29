from django.urls import path
from .views import main, mtransaction, stransactions, balance, sbalance, CustomLoginView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', main, name='main'),
    path('transaction', mtransaction, name='mtransaction'),
    path('stransaction', stransactions, name='stransaction'),
    path('balance', balance, name='balance'),
    path('balance/<str:account>/<str:currency>', sbalance, name='sbalance'),
]
