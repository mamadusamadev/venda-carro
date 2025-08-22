from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about,name='about'),
    path("sevices", views.services, name="services"),
    path("contacts", views.contacts, name="contacts"),
    path("cars", views.cars, name="cars"),
    path("carro/<uuid:car_id>/", views.car_detail, name="car_detail"),
    path("toggle-favorite/", views.toggle_favorite, name="toggle_favorite"),
]
