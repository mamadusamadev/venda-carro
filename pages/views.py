from forms.team_form import TeamForm
from entities.teams import Team
from django.shortcuts import render, redirect
from service import team_service
from django.views.generic import CreateView, TemplateView




def home(request):
    from cars.models import Car, Brand
    
    teams = team_service.list_team()
    
    # Carros em destaque (máximo 6)
    try:
        featured_cars = Car.objects.filter(
            status='active', 
            featured=True
        ).select_related('brand', 'car_model', 'seller').prefetch_related('photos')[:6]
    except Exception as e:
        # Fallback: usar os carros mais recentes como destaque
        featured_cars = Car.objects.filter(
            status='active'
        ).select_related('brand', 'car_model', 'seller').prefetch_related('photos')[:6]
    
    # Carros mais recentes (máximo 6)
    latest_cars = Car.objects.filter(
        status='active'
    ).select_related('brand', 'car_model', 'seller').prefetch_related('photos').order_by('-created_at')[:6]
    
    # Total de carros disponíveis
    total_cars = Car.objects.filter(status='active').count()
    
    # Dados para o formulário de pesquisa
    brands = Brand.objects.filter(is_active=True).order_by('name')[:10]  # Top 10 marcas
    years = range(2024, 2010, -1)  # Últimos 15 anos

    context = {
        "teams": teams,
        "featured_cars": featured_cars,
        "latest_cars": latest_cars,
        "total_cars": total_cars,
        "brands": brands,
        "years": years,
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
    from cars.models import Car, Brand
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Buscar carros ativos, reservados e vendidos (públicos)
    cars = Car.objects.filter(status__in=['active', 'reserved', 'sold']).select_related('brand', 'car_model', 'seller').prefetch_related('photos')
    
    # Filtros
    brand_id = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    fuel_type = request.GET.get('fuel_type')
    year = request.GET.get('year')
    search = request.GET.get('search')
    
    if brand_id:
        cars = cars.filter(brand_id=brand_id)
    
    if min_price:
        try:
            cars = cars.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            cars = cars.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)
    
    if year:
        try:
            cars = cars.filter(year=int(year))
        except ValueError:
            pass
    
    if search:
        cars = cars.filter(
            Q(title__icontains=search) |
            Q(brand__name__icontains=search) |
            Q(car_model__name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Ordenação
    order_by = request.GET.get('order_by', '-created_at')
    valid_orders = ['-created_at', 'created_at', 'price', '-price', 'year', '-year', 'mileage', '-mileage']
    if order_by in valid_orders:
        cars = cars.order_by(order_by)
    
    # Paginação
    paginator = Paginator(cars, 12)  # 12 carros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    brands = Brand.objects.filter(is_active=True).order_by('name')
    fuel_choices = Car.FUEL_CHOICES
    years = range(2024, 1990, -1)
    
    context = {
        'page_obj': page_obj,
        'brands': brands,
        'fuel_choices': fuel_choices,
        'years': years,
        'current_filters': {
            'brand': brand_id,
            'min_price': min_price,
            'max_price': max_price,
            'fuel_type': fuel_type,
            'year': year,
            'search': search,
            'order_by': order_by,
        }
    }
    
    return render(request, "pages/cars.html", context)


def car_detail(request):
    return render(request, "pages/car-details.html")



