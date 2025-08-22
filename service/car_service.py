from cars.models import Car, Brand, CarModel, CarPhoto
from django.shortcuts import get_object_or_404
from django.db.models import Q


def cadastrar_car(car_entity):
    """Cadastrar um novo carro"""
    car = Car.objects.create(
        title=car_entity.title,
        description=car_entity.description,
        brand=car_entity.brand,
        car_model=car_entity.car_model,
        year=car_entity.year,
        condition=car_entity.condition,
        price=car_entity.price,
        original_price=car_entity.original_price,
        negotiable=car_entity.negotiable,
        mileage=car_entity.mileage,
        fuel_type=car_entity.fuel_type,
        transmission=car_entity.transmission,
        engine_size=car_entity.engine_size,
        doors=car_entity.doors,
        seats=car_entity.seats,
        color=car_entity.color,
        license_plate=car_entity.license_plate,
        registration_date=car_entity.registration_date,
        inspection_valid_until=car_entity.inspection_valid_until,
        insurance_valid_until=car_entity.insurance_valid_until,
        city=car_entity.city,
        district=car_entity.district,
        postal_code=car_entity.postal_code,
        seller=car_entity.seller,
        status=car_entity.status,
        featured=car_entity.featured,
        air_conditioning=car_entity.air_conditioning,
        abs_brakes=car_entity.abs_brakes,
        airbags=car_entity.airbags,
        backup_camera=car_entity.backup_camera,
        bluetooth=car_entity.bluetooth,
        central_locking=car_entity.central_locking,
        electric_windows=car_entity.electric_windows,
        gps=car_entity.gps,
        leather_seats=car_entity.leather_seats,
        parking_sensors=car_entity.parking_sensors,
        power=car_entity.power,
        version=car_entity.version
    )
    return car


def listar_cars():
    """Listar todos os carros"""
    return Car.objects.all().select_related('brand', 'car_model', 'seller').prefetch_related('photos')


def listar_cars_ativos():
    """Listar carros ativos"""
    return Car.objects.filter(status='active').select_related('brand', 'car_model', 'seller').prefetch_related('photos')


def listar_cars_em_destaque():
    """Listar carros em destaque"""
    return Car.objects.filter(status='active', featured=True).select_related('brand', 'car_model', 'seller').prefetch_related('photos')


def listar_cars_recentes(limit=6):
    """Listar carros mais recentes"""
    return Car.objects.filter(status='active').select_related('brand', 'car_model', 'seller').prefetch_related('photos').order_by('-created_at')[:limit]


def listar_car_id(id):
    """Buscar carro por ID"""
    return get_object_or_404(
        Car.objects.select_related('brand', 'car_model', 'seller')
               .prefetch_related('photos', 'reviews', 'reviews__buyer'),
        id=id
    )


def listar_cars_vendedor(seller):
    """Listar carros de um vendedor"""
    return Car.objects.filter(seller=seller).select_related('brand', 'car_model').prefetch_related('photos')


def listar_cars_similares(car, limit=4):
    """Listar carros similares (mesma marca)"""
    return Car.objects.filter(
        brand=car.brand,
        status='active'
    ).exclude(id=car.id).select_related('brand', 'car_model', 'seller').prefetch_related('photos')[:limit]


def pesquisar_cars(search_query=None, brand=None, fuel_type=None, year=None, max_price=None, 
                  min_price=None, city=None, transmission=None, condition=None):
    """Pesquisar carros com filtros"""
    cars = Car.objects.filter(status='active')
    
    if search_query:
        cars = cars.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(car_model__name__icontains=search_query)
        )
    
    if brand:
        cars = cars.filter(brand_id=brand)
    
    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)
    
    if year:
        cars = cars.filter(year=year)
    
    if max_price:
        cars = cars.filter(price__lte=max_price)
    
    if min_price:
        cars = cars.filter(price__gte=min_price)
    
    if city:
        cars = cars.filter(city__icontains=city)
    
    if transmission:
        cars = cars.filter(transmission=transmission)
    
    if condition:
        cars = cars.filter(condition=condition)
    
    return cars.select_related('brand', 'car_model', 'seller').prefetch_related('photos')


def editar_car(car_bd, car_entity):
    """Editar um carro existente"""
    car_bd.title = car_entity.title
    car_bd.description = car_entity.description
    car_bd.brand = car_entity.brand
    car_bd.car_model = car_entity.car_model
    car_bd.year = car_entity.year
    car_bd.condition = car_entity.condition
    car_bd.price = car_entity.price
    car_bd.original_price = car_entity.original_price
    car_bd.negotiable = car_entity.negotiable
    car_bd.mileage = car_entity.mileage
    car_bd.fuel_type = car_entity.fuel_type
    car_bd.transmission = car_entity.transmission
    car_bd.engine_size = car_entity.engine_size
    car_bd.doors = car_entity.doors
    car_bd.seats = car_entity.seats
    car_bd.color = car_entity.color
    car_bd.license_plate = car_entity.license_plate
    car_bd.registration_date = car_entity.registration_date
    car_bd.inspection_valid_until = car_entity.inspection_valid_until
    car_bd.insurance_valid_until = car_entity.insurance_valid_until
    car_bd.city = car_entity.city
    car_bd.district = car_entity.district
    car_bd.postal_code = car_entity.postal_code
    car_bd.status = car_entity.status
    car_bd.featured = car_entity.featured
    car_bd.air_conditioning = car_entity.air_conditioning
    car_bd.abs_brakes = car_entity.abs_brakes
    car_bd.airbags = car_entity.airbags
    car_bd.backup_camera = car_entity.backup_camera
    car_bd.bluetooth = car_entity.bluetooth
    car_bd.central_locking = car_entity.central_locking
    car_bd.electric_windows = car_entity.electric_windows
    car_bd.gps = car_entity.gps
    car_bd.leather_seats = car_entity.leather_seats
    car_bd.parking_sensors = car_entity.parking_sensors
    car_bd.power = car_entity.power
    car_bd.version = car_entity.version
    car_bd.save(force_update=True)
    return car_bd


def alterar_status_car(car_bd, novo_status):
    """Alterar status do carro"""
    car_bd.status = novo_status
    car_bd.save(update_fields=['status'])
    return car_bd


def remover_car(car_bd):
    """Remover um carro"""
    car_bd.delete()


def incrementar_visualizacoes(car_bd):
    """Incrementar visualizações do carro"""
    car_bd.views += 1
    car_bd.save(update_fields=['views'])


def adicionar_foto_car(car_bd, foto, is_main=False, caption=''):
    """Adicionar foto ao carro"""
    if is_main:
        # Remove foto principal anterior
        CarPhoto.objects.filter(car=car_bd, is_main=True).update(is_main=False)
    
    car_photo = CarPhoto.objects.create(
        car=car_bd,
        photo=foto,
        is_main=is_main,
        caption=caption
    )
    return car_photo


def listar_brands():
    """Listar todas as marcas ativas"""
    return Brand.objects.filter(is_active=True).order_by('name')


def listar_models_por_brand(brand_id):
    """Listar modelos por marca"""
    return CarModel.objects.filter(brand_id=brand_id, is_active=True).order_by('name')


def contar_cars_ativos():
    """Contar total de carros ativos"""
    return Car.objects.filter(status='active').count()


def contar_cars_vendedor(seller):
    """Contar carros de um vendedor"""
    return Car.objects.filter(seller=seller).count()


def obter_estatisticas_vendedor(seller):
    """Obter estatísticas do vendedor"""
    cars = Car.objects.filter(seller=seller)
    return {
        'total': cars.count(),
        'ativos': cars.filter(status='active').count(),
        'vendidos': cars.filter(status='sold').count(),
        'reservados': cars.filter(status='reserved').count(),
        'total_visualizacoes': sum(car.views for car in cars)
    }


def listar_cars_recentes_vendedor(seller, limit=6):
    """Listar carros recentes de um vendedor"""
    return Car.objects.filter(seller=seller).order_by('-created_at')[:limit] 