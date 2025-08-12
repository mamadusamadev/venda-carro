from forms.team_form import TeamForm
from entities.teams import Team
from django.shortcuts import render, redirect
from service import team_service



# Create your views here.


def home(request):
    teams = team_service.list_team()

    context = {
        "teams": teams
    }

    return render(request, 'pages/home.html', context)



def about(request):
    teams = team_service.list_team()

    context = {
        "teams": teams
    }

    return render(request, "pages/about.html", context)


def services(request):
    return render(request, "pages/services.html")


def contacts(request):
    return render(request, "pages/contacts.html")


def cars(request):
    return render(request, "pages/cars.html")



