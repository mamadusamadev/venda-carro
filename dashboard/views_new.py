from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from uuid import UUID

from forms.car_forms import CarForm, CarSearchForm
from service.car_service import CarService
from entities.car_entity import CarEntity, CarSearchFilters
from cars.models import Car, Brand, CarModel


@login_required
def car_add_new(request):
    """View para adicionar carro com suporte a múltiplas imagens"""
    
    # Verifica se o utilizador pode vender carros
    if not request.user.is_seller():
        messages.error(request, 'Apenas vendedores podem adicionar carros.')
        return redirect('dashboard:home')
    
    form = CarForm()
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Cria entidade com dados do formulário
            car_entity = CarEntity(
                title=form.cleaned_data['title'],
                brand_name=form.cleaned_data['brand'].name,
                model_name=form.cleaned_data['car_model'].name,
                year=form.cleaned_data['year'],
                price=form.cleaned_data['price'],
                mileage=form.cleaned_data['mileage'],
                fuel_type=form.cleaned_data['fuel_type'],
                transmission=form.cleaned_data['transmission'],
                engine_size=form.cleaned_data['engine_size'],
                power=form.cleaned_data['power'],
                doors=int(form.cleaned_data['doors']),
                seats=int(form.cleaned_data['seats']),
                color=form.cleaned_data['color'],
                condition=form.cleaned_data['condition'],
                description=form.cleaned_data['description'],
                location=form.cleaned_data['location'],
                city=form.cleaned_data['city'],
                district=form.cleaned_data['district'],
                postal_code=form.cleaned_data['postal_code'],
                status=form.cleaned_data['status'],
                is_featured=form.cleaned_data['is_featured'],
                images=form.cleaned_data['images'],
                # Equipamentos
                air_conditioning=form.cleaned_data['air_conditioning'],
                power_steering=form.cleaned_data['power_steering'],
                electric_windows=form.cleaned_data['electric_windows'],
                airbags=form.cleaned_data['airbags'],
                abs_brakes=form.cleaned_data['abs_brakes'],
                alarm_system=form.cleaned_data['alarm_system'],
                alloy_wheels=form.cleaned_data['alloy_wheels'],
                cd_player=form.cleaned_data['cd_player'],
                leather_seats=form.cleaned_data['leather_seats'],
                sunroof=form.cleaned_data['sunroof'],
                gps_navigation=form.cleaned_data['gps_navigation'],
                backup_camera=form.cleaned_data['backup_camera'],
            )
            
            # Usa o service para criar o carro
            success, car, message = CarService.create_car(car_entity, request.user)
            
            if success:
                messages.success(request, message)
                return redirect('dashboard:car_detail', car_id=car.id)
            else:
                messages.error(request, message)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    
    context = {
        'form': form,
        'title': 'Adicionar Carro',
        'brands': Brand.objects.filter(is_active=True).order_by('name')
    }
    
    return render(request, 'dashboard/car_add_new.html', context)


@login_required
def car_edit_new(request, car_id):
    """View para editar carro"""
    
    try:
        car_uuid = UUID(str(car_id))
        car = CarService.get_car_by_id(car_uuid)
        
        if not car:
            messages.error(request, 'Carro não encontrado.')
            return redirect('dashboard:my_cars')
        
        # Verifica permissões
        if car.seller != request.user and not request.user.is_staff:
            messages.error(request, 'Não tem permissão para editar este carro.')
            return redirect('dashboard:my_cars')
        
        # Preenche o formulário com dados existentes
        initial_data = {
            'title': car.title,
            'brand': car.brand,
            'car_model': car.car_model,
            'year': car.year,
            'price': car.price,
            'mileage': car.mileage,
            'fuel_type': car.fuel_type,
            'transmission': car.transmission,
            'engine_size': car.engine_size,
            'power': car.power,
            'doors': car.doors,
            'seats': car.seats,
            'color': car.color,
            'condition': car.condition,
            'description': car.description,
            'location': car.location,
            'city': car.city,
            'district': car.district,
            'postal_code': car.postal_code,
            'status': car.status,
            'is_featured': car.is_featured,
            # Equipamentos
            'air_conditioning': car.air_conditioning,
            'power_steering': car.power_steering,
            'electric_windows': car.electric_windows,
            'airbags': car.airbags,
            'abs_brakes': car.abs_brakes,
            'alarm_system': car.alarm_system,
            'alloy_wheels': car.alloy_wheels,
            'cd_player': car.cd_player,
            'leather_seats': car.leather_seats,
            'sunroof': car.sunroof,
            'gps_navigation': car.gps_navigation,
            'backup_camera': car.backup_camera,
        }
        
        form = CarForm(initial=initial_data)
        
        if request.method == 'POST':
            form = CarForm(request.POST, request.FILES)
            
            if form.is_valid():
                # Cria entidade com novos dados
                car_entity = CarEntity(
                    title=form.cleaned_data['title'],
                    brand_name=form.cleaned_data['brand'].name,
                    model_name=form.cleaned_data['car_model'].name,
                    year=form.cleaned_data['year'],
                    price=form.cleaned_data['price'],
                    mileage=form.cleaned_data['mileage'],
                    fuel_type=form.cleaned_data['fuel_type'],
                    transmission=form.cleaned_data['transmission'],
                    engine_size=form.cleaned_data['engine_size'],
                    power=form.cleaned_data['power'],
                    doors=int(form.cleaned_data['doors']),
                    seats=int(form.cleaned_data['seats']),
                    color=form.cleaned_data['color'],
                    condition=form.cleaned_data['condition'],
                    description=form.cleaned_data['description'],
                    location=form.cleaned_data['location'],
                    city=form.cleaned_data['city'],
                    district=form.cleaned_data['district'],
                    postal_code=form.cleaned_data['postal_code'],
                    status=form.cleaned_data['status'],
                    is_featured=form.cleaned_data['is_featured'],
                    images=form.cleaned_data['images'],
                    # Equipamentos
                    air_conditioning=form.cleaned_data['air_conditioning'],
                    power_steering=form.cleaned_data['power_steering'],
                    electric_windows=form.cleaned_data['electric_windows'],
                    airbags=form.cleaned_data['airbags'],
                    abs_brakes=form.cleaned_data['abs_brakes'],
                    alarm_system=form.cleaned_data['alarm_system'],
                    alloy_wheels=form.cleaned_data['alloy_wheels'],
                    cd_player=form.cleaned_data['cd_player'],
                    leather_seats=form.cleaned_data['leather_seats'],
                    sunroof=form.cleaned_data['sunroof'],
                    gps_navigation=form.cleaned_data['gps_navigation'],
                    backup_camera=form.cleaned_data['backup_camera'],
                )
                
                # Usa o service para atualizar
                success, updated_car, message = CarService.update_car(car_uuid, car_entity, request.user)
                
                if success:
                    messages.success(request, message)
                    return redirect('dashboard:car_detail', car_id=updated_car.id)
                else:
                    messages.error(request, message)
            else:
                messages.error(request, 'Por favor, corrija os erros abaixo.')
        
        context = {
            'form': form,
            'car': car,
            'title': f'Editar {car.title}',
            'brands': Brand.objects.filter(is_active=True).order_by('name'),
            'existing_images': car.photos.all().order_by('order')
        }
        
        return render(request, 'dashboard/car_edit_new.html', context)
        
    except ValueError:
        messages.error(request, 'ID de carro inválido.')
        return redirect('dashboard:my_cars')


@login_required
def car_list_new(request):
    """View para listar carros com filtros avançados"""
    
    form = CarSearchForm(request.GET)
    cars = []
    
    if form.is_valid():
        # Cria filtros baseados no formulário
        filters = CarSearchFilters(
            search_term=form.cleaned_data.get('search', ''),
            brand_id=form.cleaned_data.get('brand').id if form.cleaned_data.get('brand') else None,
            min_price=form.cleaned_data.get('min_price'),
            max_price=form.cleaned_data.get('max_price'),
            min_year=form.cleaned_data.get('min_year'),
            max_year=form.cleaned_data.get('max_year'),
            fuel_type=form.cleaned_data.get('fuel_type', ''),
            transmission=form.cleaned_data.get('transmission', ''),
            city=form.cleaned_data.get('city', ''),
            status='active'
        )
        
        # Usa o service para pesquisar
        cars = CarService.search_cars(filters)
    else:
        # Se não há filtros, mostra todos os carros ativos
        filters = CarSearchFilters(status='active')
        cars = CarService.search_cars(filters)
    
    # Paginação
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page', 1)
    cars_page = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'cars': cars_page,
        'total_cars': cars.count(),
        'title': 'Todos os Carros'
    }
    
    return render(request, 'dashboard/car_list_new.html', context)


@csrf_exempt
def get_car_models_ajax(request):
    """AJAX endpoint para obter modelos baseados na marca"""
    
    if request.method == 'POST':
        brand_id = request.POST.get('brand_id')
        
        if brand_id:
            models = CarService.get_models_by_brand(int(brand_id))
            models_data = [
                {'id': model.id, 'name': model.name}
                for model in models
            ]
            return JsonResponse({'models': models_data})
    
    return JsonResponse({'models': []})


@login_required
@require_http_methods(["POST"])
def delete_car_image(request, image_id):
    """AJAX endpoint para eliminar imagem de carro"""
    
    success, message = CarService.delete_car_image(image_id, request.user)
    
    return JsonResponse({
        'success': success,
        'message': message
    })


@login_required
def my_cars_new(request):
    """View para mostrar carros do utilizador atual"""
    
    if not request.user.is_seller():
        messages.error(request, 'Apenas vendedores podem gerir carros.')
        return redirect('dashboard:home')
    
    cars = CarService.get_user_cars(request.user)
    
    # Estatísticas
    stats = {
        'total': cars.count(),
        'active': cars.filter(status='active').count(),
        'sold': cars.filter(status='sold').count(),
        'inactive': cars.filter(status='inactive').count(),
    }
    
    # Paginação
    paginator = Paginator(cars, 10)
    page_number = request.GET.get('page', 1)
    cars_page = paginator.get_page(page_number)
    
    context = {
        'cars': cars_page,
        'stats': stats,
        'title': 'Os Meus Carros'
    }
    
    return render(request, 'dashboard/my_cars_new.html', context) 