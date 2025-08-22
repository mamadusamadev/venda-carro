from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json

from forms.car_forms import CarSearchForm
from entities.car_entity import Car as CarEntity
from service import car_service, team_service
from cars.models import Car


def home(request):
    """Página inicial"""
    teams = team_service.list_team()
    try:
        featured_cars = Car.objects.filter(
            status='active',
            featured=True
        ).select_related('brand', 'car_model', 'seller').prefetch_related('photos')[:6]
    except Exception as e:
        featured_cars = Car.objects.filter(
            status='active'
        ).select_related('brand', 'car_model', 'seller').prefetch_related('photos')[:6]
    
    latest_cars = Car.objects.filter(
        status='active'
    ).select_related('brand', 'car_model', 'seller').prefetch_related('photos').order_by('-created_at')[:6]
    
    total_cars = Car.objects.filter(status='active').count()
    
    from cars.models import Brand
    brands = Brand.objects.filter(is_active=True).order_by('name')[:10]
    years = range(2024, 2010, -1)
    
    context = {
        "teams": teams,
        "featured_cars": featured_cars,
        "latest_cars": latest_cars,
        "total_cars": total_cars,
        "brands": brands,
        "years": years,
    }
    
    return render(request, 'pages/home.html', context)


def car_detail(request, car_id):
    """Página de detalhes do carro"""
    car = get_object_or_404(Car, id=car_id, status__in=['active', 'reserved', 'sold'])
    
    # Incrementar visualizações
    car.views += 1
    car.save()
    
    # Carros similares
    similar_cars = Car.objects.filter(
        brand=car.brand,
        status='active'
    ).exclude(id=car.id).select_related('brand', 'car_model').prefetch_related('photos')[:4]
    
    # Verificar se é favorito
    is_favorite = False
    if request.user.is_authenticated:
        from cars.models import Favorite
        is_favorite = Favorite.objects.filter(user=request.user, car=car).exists()
    
    # Calcular média de avaliações
    reviews = car.reviews.all()
    avg_rating = 0
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = round(total_rating / len(reviews), 1)
    
    context = {
        'car': car,
        'similar_cars': similar_cars,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'reviews_count': len(reviews),
    }
    
    return render(request, 'pages/car-details.html', context)


def about(request):
    """Página sobre"""
    teams = team_service.list_team()

    context = {
        "teams": teams
    }

    return render(request, 'pages/about.html', context)


def services(request):
    """Página de serviços"""
    context = {}
    return render(request, 'pages/services.html', context)


def contacts(request):
    """Página de contactos"""
    context = {}
    return render(request, 'pages/contacts.html', context)


def cars(request):
    """Página de listagem de carros com filtros"""
    form = CarSearchForm(request.GET or None)
    
    # Parâmetros de pesquisa
    search_query = request.GET.get('search', '')
    brand = request.GET.get('brand', '')
    fuel_type = request.GET.get('fuel_type', '')
    year = request.GET.get('year', '')
    max_price = request.GET.get('max_price', '')
    min_price = request.GET.get('min_price', '')
    city = request.GET.get('city', '')
    transmission = request.GET.get('transmission', '')
    condition = request.GET.get('condition', '')
    order_by = request.GET.get('order_by', '-created_at')
    
    # Converter valores vazios para None
    brand = brand if brand else None
    fuel_type = fuel_type if fuel_type else None
    year = int(year) if year else None
    max_price = float(max_price) if max_price else None
    min_price = float(min_price) if min_price else None
    city = city if city else None
    transmission = transmission if transmission else None
    condition = condition if condition else None
    
    # Pesquisar carros
    cars = car_service.pesquisar_cars(
        search_query=search_query,
        brand=brand,
        fuel_type=fuel_type,
        year=year,
        max_price=max_price,
        min_price=min_price,
        city=city,
        transmission=transmission,
        condition=condition
    )
    
    # Ordenação
    if order_by == 'price_asc':
        cars = cars.order_by('price')
    elif order_by == 'price_desc':
        cars = cars.order_by('-price')
    elif order_by == 'year_desc':
        cars = cars.order_by('-year')
    elif order_by == 'year_asc':
        cars = cars.order_by('year')
    elif order_by == 'mileage_asc':
        cars = cars.order_by('mileage')
    elif order_by == 'mileage_desc':
        cars = cars.order_by('-mileage')
    else:  # default: -created_at
        cars = cars.order_by('-created_at')
    
    # Paginação
    paginator = Paginator(cars, 12)  # 12 carros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    brands = car_service.listar_brands()
    years_range = range(2024, 1999, -1)
    
    # Favoritos do utilizador (se autenticado)
    user_favorites = []
    if request.user.is_authenticated:
        from cars.models import Favorite
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('car_id', flat=True))
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'cars': page_obj,
        'brands': brands,
        'years_range': years_range,
        'search_query': search_query,
        'user_favorites': user_favorites,
        'fuel_choices': Car.FUEL_CHOICES,
        'years': years_range,
        'current_filters': {
            'brand': brand,
            'fuel_type': fuel_type,
            'year': year,
            'max_price': max_price,
            'min_price': min_price,
            'city': city,
            'transmission': transmission,
            'condition': condition,
            'order_by': order_by
        }
    }
    
    return render(request, 'pages/cars.html', context)


@login_required
@require_POST
def toggle_favorite(request):
    """Toggle favorito de um carro"""
    try:
        print(f"Toggle favorite - User: {request.user}, Method: {request.method}")
        print(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        car_id = data.get('car_id')
        
        print(f"Car ID recebido: {car_id}")
        
        if not car_id:
            return JsonResponse({'success': False, 'message': 'ID do carro não fornecido'})
        
        car = get_object_or_404(Car, id=car_id)
        print(f"Carro encontrado: {car.title}")
        
        from cars.models import Favorite
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            car=car
        )
        
        if not created:
            # Se já existia, remove
            favorite.delete()
            is_favorite = False
            message = 'Removido dos favoritos'
            print(f"Favorito removido para carro {car_id}")
        else:
            # Se não existia, foi criado
            is_favorite = True
            message = 'Adicionado aos favoritos'
            print(f"Favorito adicionado para carro {car_id}")
        
        response_data = {
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        }
        print(f"Resposta: {response_data}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Erro no toggle_favorite: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        })




