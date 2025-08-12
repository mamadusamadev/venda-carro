from forms.team_form import TeamForm
from entities.teams import Team
from django.shortcuts import render, redirect
from service import team_service
from django.views.generic import CreateView, TemplateView


# Create your views here.
class HomeView(TemplateView):
    """
    Página inicial com opções de registro
    """
    template_name = 'registration/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_cars'] = Car.objects.filter(status='available')[:6]
        return context


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


def car_detail(request):
    return render(request, "pages/car-details.html")



def register(request):
    return render(request, "pages/register.html")



def login(request):
    return render(request, "pages/login.html")