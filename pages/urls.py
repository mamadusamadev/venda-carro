from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about,name='about'),
    path("sevices", views.services, name="services"),
    path("contacts", views.contacts, name="contacts"),
    path("cars", views.cars, name="cars"),
    path("detail", views.car_detail, name="detail"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    
    
]
