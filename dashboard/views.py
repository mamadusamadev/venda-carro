from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import json

from cars.models import Car, Brand, CarModel, CarPhoto, Favorite, Review, Message, PriceHistory
from accounts.models import User


@login_required
def dashboard_home(request):
    """
    Página principal do dashboard com estatísticas gerais
    """
    # Estatísticas gerais
    total_cars = Car.objects.count()
    active_cars = Car.objects.filter(status='active').count()
    sold_cars = Car.objects.filter(status='sold').count()
    total_users = User.objects.count()
    
    # Estatísticas do utilizador atual
    user_cars = Car.objects.filter(seller=request.user).count()
    user_favorites = Favorite.objects.filter(user=request.user).count()
    user_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    # Carros recentes
    recent_cars = Car.objects.filter(status='active').order_by('-created_at')[:5]
    
    # Marcas mais populares
    popular_brands = Brand.objects.annotate(
        car_count=Count('car')
    ).order_by('-car_count')[:5]
    
    # Estatísticas por mês (últimos 6 meses)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_stats = []
    
    for i in range(6):
        month_start = six_months_ago + timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        cars_created = Car.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%B'),
            'cars': cars_created
        })
    
    context = {
        'total_cars': total_cars,
        'active_cars': active_cars,
        'sold_cars': sold_cars,
        'total_users': total_users,
        'user_cars': user_cars,
        'user_favorites': user_favorites,
        'user_messages': user_messages,
        'recent_cars': recent_cars,
        'popular_brands': popular_brands,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def car_list(request):
    """
    Lista de carros com filtros e pesquisa
    """
    cars = Car.objects.select_related('brand', 'car_model', 'seller').all()
    
    # Filtros
    brand_id = request.GET.get('brand')
    status = request.GET.get('status')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search')
    fuel_type = request.GET.get('fuel_type')
    year = request.GET.get('year')
    
    if brand_id:
        cars = cars.filter(brand_id=brand_id)
    
    if status:
        cars = cars.filter(status=status)
    
    if min_price:
        cars = cars.filter(price__gte=min_price)
    
    if max_price:
        cars = cars.filter(price__lte=max_price)
    
    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)
    
    if year:
        cars = cars.filter(year=year)
    
    if search:
        cars = cars.filter(
            Q(title__icontains=search) |
            Q(brand__name__icontains=search) |
            Q(car_model__name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Ordenação
    order_by = request.GET.get('order_by', '-created_at')
    cars = cars.order_by(order_by)
    
    # Paginação
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    brands = Brand.objects.filter(is_active=True).order_by('name')
    fuel_choices = Car.FUEL_CHOICES
    status_choices = Car.STATUS_CHOICES
    years = range(datetime.now().year, 1990, -1)
    
    context = {
        'page_obj': page_obj,
        'brands': brands,
        'fuel_choices': fuel_choices,
        'status_choices': status_choices,
        'years': years,
        'current_filters': {
            'brand': brand_id,
            'status': status,
            'min_price': min_price,
            'max_price': max_price,
            'search': search,
            'fuel_type': fuel_type,
            'year': year,
            'order_by': order_by,
        }
    }
    
    return render(request, 'dashboard/car_list.html', context)


@login_required
def car_detail(request, car_id):
    """
    Detalhes de um carro específico
    """
    car = get_object_or_404(Car, id=car_id)
    
    # Incrementar visualizações
    car.increment_views()
    
    # Fotos do carro
    photos = car.photos.all().order_by('order', 'created_at')
    
    # Histórico de preços
    price_history = car.price_history.all().order_by('-created_at')[:10]
    
    # Reviews do vendedor
    seller_reviews = Review.objects.filter(seller=car.seller).order_by('-created_at')[:5]
    
    # Carros similares
    similar_cars = Car.objects.filter(
        brand=car.brand,
        status='active'
    ).exclude(id=car.id)[:4]
    
    # Verificar se o utilizador favoritou este carro
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, car=car).exists()
    
    context = {
        'car': car,
        'photos': photos,
        'price_history': price_history,
        'seller_reviews': seller_reviews,
        'similar_cars': similar_cars,
        'is_favorited': is_favorited,
    }
    
    return render(request, 'dashboard/car_detail.html', context)


@login_required
def my_cars(request):
    """
    Carros do utilizador atual
    """
    cars = Car.objects.filter(seller=request.user).order_by('-created_at')
    
    # Estatísticas
    total_cars = cars.count()
    active_cars = cars.filter(status='active').count()
    sold_cars = cars.filter(status='sold').count()
    total_views = cars.aggregate(Sum('views'))['views__sum'] or 0
    total_favorites = cars.aggregate(Sum('favorites_count'))['favorites_count__sum'] or 0
    
    # Paginação
    paginator = Paginator(cars, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_cars': total_cars,
        'active_cars': active_cars,
        'sold_cars': sold_cars,
        'total_views': total_views,
        'total_favorites': total_favorites,
    }
    
    return render(request, 'dashboard/my_cars.html', context)


@login_required
def car_add(request):
    """
    Adicionar novo carro
    """
    if request.method == 'POST':
        # Processar formulário
        try:
            brand = get_object_or_404(Brand, id=request.POST.get('brand'))
            car_model = get_object_or_404(CarModel, id=request.POST.get('car_model'))
            
            car = Car.objects.create(
                seller=request.user,
                brand=brand,
                car_model=car_model,
                version=request.POST.get('version', ''),
                year=int(request.POST.get('year')),
                color=request.POST.get('color'),
                fuel_type=request.POST.get('fuel_type'),
                transmission=request.POST.get('transmission'),
                engine_size=request.POST.get('engine_size') or None,
                power=request.POST.get('power') or None,
                mileage=int(request.POST.get('mileage')),
                doors=int(request.POST.get('doors', 4)),
                seats=int(request.POST.get('seats', 5)),
                condition=request.POST.get('condition'),
                license_plate=request.POST.get('license_plate'),
                price=float(request.POST.get('price')),
                negotiable=request.POST.get('negotiable') == 'on',
                city=request.POST.get('city'),
                district=request.POST.get('district'),
                postal_code=request.POST.get('postal_code', ''),
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                
                # Equipamentos
                air_conditioning=request.POST.get('air_conditioning') == 'on',
                gps=request.POST.get('gps') == 'on',
                bluetooth=request.POST.get('bluetooth') == 'on',
                parking_sensors=request.POST.get('parking_sensors') == 'on',
                backup_camera=request.POST.get('backup_camera') == 'on',
                leather_seats=request.POST.get('leather_seats') == 'on',
                electric_windows=request.POST.get('electric_windows') == 'on',
                central_locking=request.POST.get('central_locking') == 'on',
                abs_brakes=request.POST.get('abs_brakes') == 'on',
                airbags=request.POST.get('airbags') == 'on',
                
                status='pending'
            )
            
            messages.success(request, 'Carro adicionado com sucesso! Aguarda aprovação.')
            return redirect('dashboard:car_detail', car_id=car.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar carro: {str(e)}')
    
    # Dados para o formulário
    brands = Brand.objects.filter(is_active=True).order_by('name')
    fuel_choices = Car.FUEL_CHOICES
    transmission_choices = Car.TRANSMISSION_CHOICES
    condition_choices = Car.CONDITION_CHOICES
    door_choices = Car.DOOR_CHOICES
    years = range(datetime.now().year + 1, 1990, -1)
    
    context = {
        'brands': brands,
        'fuel_choices': fuel_choices,
        'transmission_choices': transmission_choices,
        'condition_choices': condition_choices,
        'door_choices': door_choices,
        'years': years,
    }
    
    return render(request, 'dashboard/car_add.html', context)


@login_required
def car_edit(request, car_id):
    """
    Editar carro existente
    """
    car = get_object_or_404(Car, id=car_id, seller=request.user)
    
    if request.method == 'POST':
        try:
            # Registar mudança de preço se necessário
            old_price = car.price
            new_price = float(request.POST.get('price'))
            
            if old_price != new_price:
                PriceHistory.objects.create(
                    car=car,
                    old_price=old_price,
                    new_price=new_price,
                    change_reason=request.POST.get('price_change_reason', 'Alteração manual')
                )
            
            # Atualizar carro
            brand = get_object_or_404(Brand, id=request.POST.get('brand'))
            car_model = get_object_or_404(CarModel, id=request.POST.get('car_model'))
            
            car.brand = brand
            car.car_model = car_model
            car.version = request.POST.get('version', '')
            car.year = int(request.POST.get('year'))
            car.color = request.POST.get('color')
            car.fuel_type = request.POST.get('fuel_type')
            car.transmission = request.POST.get('transmission')
            car.engine_size = request.POST.get('engine_size') or None
            car.power = request.POST.get('power') or None
            car.mileage = int(request.POST.get('mileage'))
            car.doors = int(request.POST.get('doors', 4))
            car.seats = int(request.POST.get('seats', 5))
            car.condition = request.POST.get('condition')
            car.license_plate = request.POST.get('license_plate')
            car.price = new_price
            car.negotiable = request.POST.get('negotiable') == 'on'
            car.city = request.POST.get('city')
            car.district = request.POST.get('district')
            car.postal_code = request.POST.get('postal_code', '')
            car.title = request.POST.get('title')
            car.description = request.POST.get('description')
            
            # Equipamentos
            car.air_conditioning = request.POST.get('air_conditioning') == 'on'
            car.gps = request.POST.get('gps') == 'on'
            car.bluetooth = request.POST.get('bluetooth') == 'on'
            car.parking_sensors = request.POST.get('parking_sensors') == 'on'
            car.backup_camera = request.POST.get('backup_camera') == 'on'
            car.leather_seats = request.POST.get('leather_seats') == 'on'
            car.electric_windows = request.POST.get('electric_windows') == 'on'
            car.central_locking = request.POST.get('central_locking') == 'on'
            car.abs_brakes = request.POST.get('abs_brakes') == 'on'
            car.airbags = request.POST.get('airbags') == 'on'
            
            car.save()
            
            messages.success(request, 'Carro atualizado com sucesso!')
            return redirect('dashboard:car_detail', car_id=car.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar carro: {str(e)}')
    
    # Dados para o formulário
    brands = Brand.objects.filter(is_active=True).order_by('name')
    models = CarModel.objects.filter(brand=car.brand, is_active=True).order_by('name')
    fuel_choices = Car.FUEL_CHOICES
    transmission_choices = Car.TRANSMISSION_CHOICES
    condition_choices = Car.CONDITION_CHOICES
    door_choices = Car.DOOR_CHOICES
    years = range(datetime.now().year + 1, 1990, -1)
    
    context = {
        'car': car,
        'brands': brands,
        'models': models,
        'fuel_choices': fuel_choices,
        'transmission_choices': transmission_choices,
        'condition_choices': condition_choices,
        'door_choices': door_choices,
        'years': years,
    }
    
    return render(request, 'dashboard/car_edit.html', context)


@login_required
@require_http_methods(["POST"])
def car_delete(request, car_id):
    """
    Eliminar carro
    """
    car = get_object_or_404(Car, id=car_id, seller=request.user)
    
    try:
        car_title = str(car)
        car.delete()
        messages.success(request, f'Carro "{car_title}" eliminado com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao eliminar carro: {str(e)}')
    
    return redirect('dashboard:my_cars')


@login_required
def toggle_favorite(request, car_id):
    """
    Adicionar/remover carro dos favoritos (AJAX)
    """
    if request.method == 'POST':
        car = get_object_or_404(Car, id=car_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, car=car)
        
        if not created:
            favorite.delete()
            is_favorited = False
        else:
            is_favorited = True
        
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'favorites_count': car.favorites_count
        })
    
    return JsonResponse({'success': False})


@login_required
def get_car_models(request):
    """
    Obter modelos de uma marca (AJAX)
    """
    brand_id = request.GET.get('brand_id')
    if brand_id:
        models = CarModel.objects.filter(brand_id=brand_id, is_active=True).order_by('name')
        model_list = [{'id': model.id, 'name': model.name} for model in models]
        return JsonResponse({'models': model_list})
    
    return JsonResponse({'models': []})


@login_required
def statistics(request):
    """
    Página de estatísticas detalhadas
    """
    # Estatísticas gerais
    total_cars = Car.objects.count()
    active_cars = Car.objects.filter(status='active').count()
    sold_cars = Car.objects.filter(status='sold').count()
    
    # Estatísticas por marca
    brand_stats = Brand.objects.annotate(
        car_count=Count('car'),
        avg_price=Avg('car__price')
    ).order_by('-car_count')[:10]
    
    # Estatísticas por combustível
    fuel_stats = Car.objects.values('fuel_type').annotate(
        count=Count('id'),
        avg_price=Avg('price')
    ).order_by('-count')
    
    # Estatísticas por ano
    year_stats = Car.objects.values('year').annotate(
        count=Count('id'),
        avg_price=Avg('price')
    ).order_by('-year')[:10]
    
    # Preços médios por distrito
    district_stats = Car.objects.values('district').annotate(
        count=Count('id'),
        avg_price=Avg('price')
    ).order_by('-avg_price')[:10]
    
    context = {
        'total_cars': total_cars,
        'active_cars': active_cars,
        'sold_cars': sold_cars,
        'brand_stats': brand_stats,
        'fuel_stats': fuel_stats,
        'year_stats': year_stats,
        'district_stats': district_stats,
    }
    
    return render(request, 'dashboard/statistics.html', context)
