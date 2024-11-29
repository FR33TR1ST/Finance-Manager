from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import inicio_view, custom_logout
from django.contrib.auth import views as auth_views

# Create your views here.
urlpatterns = [
    path('', inicio_view, name='login'),
    path('logout/', custom_logout, name='logout'),]
