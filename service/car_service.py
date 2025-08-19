from typing import List, Optional, Tuple
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth import get_user_model
from uuid import UUID

from cars.models import Car, Brand, CarModel, CarPhoto
from entities.car_entity import CarEntity, CarSearchFilters

User = get_user_model()


class CarService:
    """Service responsável pela gestão de carros"""
    
    @staticmethod
    def create_car(car_data: CarEntity, seller: User) -> Tuple[bool, Optional[Car], str]:
        """
        Cria um novo carro com imagens
        
        Args:
            car_data: Dados do carro
            seller: Utilizador vendedor
            
        Returns:
            Tuple[bool, Optional[Car], str]: (sucesso, carro, mensagem)
        """
        try:
            # Validações
            if not seller.is_seller():
                return False, None, "Apenas vendedores podem adicionar carros"
            
            # Busca marca e modelo
            try:
                brand = Brand.objects.get(name=car_data.brand_name)
                car_model = CarModel.objects.get(name=car_data.model_name, brand=brand)
            except (Brand.DoesNotExist, CarModel.DoesNotExist):
                return False, None, "Marca ou modelo não encontrado"
            
            # Cria o carro numa transação
            with transaction.atomic():
                car = Car.objects.create(
                    title=car_data.title,
                    brand=brand,
                    car_model=car_model,
                    year=car_data.year,
                    price=car_data.price,
                    mileage=car_data.mileage,
                    fuel_type=car_data.fuel_type,
                    transmission=car_data.transmission,
                    engine_size=car_data.engine_size,
                    power=car_data.power,
                    doors=car_data.doors,
                    seats=car_data.seats,
                    color=car_data.color,
                    condition=car_data.condition,
                    description=car_data.description,
                    location=car_data.location,
                    city=car_data.city,
                    district=car_data.district,
                    postal_code=car_data.postal_code,
                    status=car_data.status,
                    is_featured=car_data.is_featured,
                    seller=seller,
                    # Equipamentos
                    air_conditioning=car_data.air_conditioning,
                    power_steering=car_data.power_steering,
                    electric_windows=car_data.electric_windows,
                    airbags=car_data.airbags,
                    abs_brakes=car_data.abs_brakes,
                    alarm_system=car_data.alarm_system,
                    alloy_wheels=car_data.alloy_wheels,
                    cd_player=car_data.cd_player,
                    leather_seats=car_data.leather_seats,
                    sunroof=car_data.sunroof,
                    gps_navigation=car_data.gps_navigation,
                    backup_camera=car_data.backup_camera,
                )
                
                # Adiciona as imagens
                if car_data.images:
                    CarService._add_car_images(car, car_data.images)
                
                return True, car, "Carro criado com sucesso"
                
        except Exception as e:
            return False, None, f"Erro ao criar carro: {str(e)}"
    
    @staticmethod
    def update_car(car_id: UUID, car_data: CarEntity, user: User) -> Tuple[bool, Optional[Car], str]:
        """
        Atualiza um carro existente
        
        Args:
            car_id: ID do carro
            car_data: Novos dados do carro
            user: Utilizador que está a editar
            
        Returns:
            Tuple[bool, Optional[Car], str]: (sucesso, carro, mensagem)
        """
        try:
            car = Car.objects.get(id=car_id)
            
            # Verifica se o utilizador pode editar
            if car.seller != user and not user.is_staff:
                return False, None, "Não tem permissão para editar este carro"
            
            # Busca marca e modelo se alterados
            if car_data.brand_name and car_data.model_name:
                try:
                    brand = Brand.objects.get(name=car_data.brand_name)
                    car_model = CarModel.objects.get(name=car_data.model_name, brand=brand)
                    car.brand = brand
                    car.car_model = car_model
                except (Brand.DoesNotExist, CarModel.DoesNotExist):
                    return False, None, "Marca ou modelo não encontrado"
            
            # Atualiza os campos
            with transaction.atomic():
                car.title = car_data.title or car.title
                car.year = car_data.year or car.year
                car.price = car_data.price or car.price
                car.mileage = car_data.mileage or car.mileage
                car.fuel_type = car_data.fuel_type or car.fuel_type
                car.transmission = car_data.transmission or car.transmission
                car.engine_size = car_data.engine_size or car.engine_size
                car.power = car_data.power or car.power
                car.doors = car_data.doors or car.doors
                car.seats = car_data.seats or car.seats
                car.color = car_data.color or car.color
                car.condition = car_data.condition or car.condition
                car.description = car_data.description or car.description
                car.location = car_data.location or car.location
                car.city = car_data.city or car.city
                car.district = car_data.district or car.district
                car.postal_code = car_data.postal_code or car.postal_code
                car.status = car_data.status or car.status
                
                # Atualiza equipamentos
                car.air_conditioning = car_data.air_conditioning
                car.power_steering = car_data.power_steering
                car.electric_windows = car_data.electric_windows
                car.airbags = car_data.airbags
                car.abs_brakes = car_data.abs_brakes
                car.alarm_system = car_data.alarm_system
                car.alloy_wheels = car_data.alloy_wheels
                car.cd_player = car_data.cd_player
                car.leather_seats = car_data.leather_seats
                car.sunroof = car_data.sunroof
                car.gps_navigation = car_data.gps_navigation
                car.backup_camera = car_data.backup_camera
                
                car.save()
                
                # Adiciona novas imagens se fornecidas
                if car_data.images:
                    CarService._add_car_images(car, car_data.images)
                
                return True, car, "Carro atualizado com sucesso"
                
        except Car.DoesNotExist:
            return False, None, "Carro não encontrado"
        except Exception as e:
            return False, None, f"Erro ao atualizar carro: {str(e)}"
    
    @staticmethod
    def delete_car(car_id: UUID, user: User) -> Tuple[bool, str]:
        """
        Elimina um carro
        
        Args:
            car_id: ID do carro
            user: Utilizador que está a eliminar
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            car = Car.objects.get(id=car_id)
            
            # Verifica permissões
            if car.seller != user and not user.is_staff:
                return False, "Não tem permissão para eliminar este carro"
            
            car.delete()
            return True, "Carro eliminado com sucesso"
            
        except Car.DoesNotExist:
            return False, "Carro não encontrado"
        except Exception as e:
            return False, f"Erro ao eliminar carro: {str(e)}"
    
    @staticmethod
    def search_cars(filters: CarSearchFilters) -> List[Car]:
        """
        Pesquisa carros com filtros
        
        Args:
            filters: Filtros de pesquisa
            
        Returns:
            List[Car]: Lista de carros encontrados
        """
        queryset = Car.objects.select_related('brand', 'car_model', 'seller').prefetch_related('photos')
        
        if filters.search_term:
            queryset = queryset.filter(
                title__icontains=filters.search_term
            )
        
        if filters.brand_id:
            queryset = queryset.filter(brand_id=filters.brand_id)
        
        if filters.model_id:
            queryset = queryset.filter(car_model_id=filters.model_id)
        
        if filters.min_price:
            queryset = queryset.filter(price__gte=filters.min_price)
        
        if filters.max_price:
            queryset = queryset.filter(price__lte=filters.max_price)
        
        if filters.min_year:
            queryset = queryset.filter(year__gte=filters.min_year)
        
        if filters.max_year:
            queryset = queryset.filter(year__lte=filters.max_year)
        
        if filters.fuel_type:
            queryset = queryset.filter(fuel_type=filters.fuel_type)
        
        if filters.transmission:
            queryset = queryset.filter(transmission=filters.transmission)
        
        if filters.city:
            queryset = queryset.filter(city__icontains=filters.city)
        
        if filters.status:
            queryset = queryset.filter(status=filters.status)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_car_by_id(car_id: UUID) -> Optional[Car]:
        """
        Busca um carro por ID
        
        Args:
            car_id: ID do carro
            
        Returns:
            Optional[Car]: Carro encontrado ou None
        """
        try:
            return Car.objects.select_related('brand', 'car_model', 'seller').prefetch_related('photos').get(id=car_id)
        except Car.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_cars(user: User) -> List[Car]:
        """
        Busca todos os carros de um utilizador
        
        Args:
            user: Utilizador
            
        Returns:
            List[Car]: Lista de carros do utilizador
        """
        return Car.objects.filter(seller=user).select_related('brand', 'car_model').prefetch_related('photos').order_by('-created_at')
    
    @staticmethod
    def _add_car_images(car: Car, images: List[UploadedFile]) -> None:
        """
        Adiciona imagens a um carro
        
        Args:
            car: Carro
            images: Lista de imagens
        """
        for index, image in enumerate(images):
            CarPhoto.objects.create(
                car=car,
                image=image,
                is_primary=(index == 0),  # Primeira imagem é a principal
                order=index + 1
            )
    
    @staticmethod
    def delete_car_image(image_id: int, user: User) -> Tuple[bool, str]:
        """
        Elimina uma imagem de carro
        
        Args:
            image_id: ID da imagem
            user: Utilizador
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            photo = CarPhoto.objects.select_related('car').get(id=image_id)
            
            # Verifica permissões
            if photo.car.seller != user and not user.is_staff:
                return False, "Não tem permissão para eliminar esta imagem"
            
            photo.delete()
            return True, "Imagem eliminada com sucesso"
            
        except CarPhoto.DoesNotExist:
            return False, "Imagem não encontrada"
        except Exception as e:
            return False, f"Erro ao eliminar imagem: {str(e)}"
    
    @staticmethod
    def get_brands_with_models() -> List[Brand]:
        """
        Retorna todas as marcas com seus modelos
        
        Returns:
            List[Brand]: Lista de marcas com modelos
        """
        return Brand.objects.filter(is_active=True).prefetch_related('models').order_by('name')
    
    @staticmethod
    def get_models_by_brand(brand_id: int) -> List[CarModel]:
        """
        Retorna modelos de uma marca específica
        
        Args:
            brand_id: ID da marca
            
        Returns:
            List[CarModel]: Lista de modelos
        """
        return CarModel.objects.filter(brand_id=brand_id, is_active=True).order_by('name') 