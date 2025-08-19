from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from django.core.files.uploadedfile import UploadedFile


class CarEntity:
    """Entidade que representa um carro"""
    
    def __init__(self, car_id=None, title="", brand_name="", model_name="", year=0, 
                 price=Decimal('0.00'), mileage=0, fuel_type="gasoline", transmission="manual",
                 engine_size="", power=0, doors=4, seats=5, color="", condition="used",
                 description="", location="", city="", district="", postal_code="",
                 status="active", is_featured=False, seller_id=None, images=None,
                 air_conditioning=False, power_steering=False, electric_windows=False,
                 airbags=False, abs_brakes=False, alarm_system=False, alloy_wheels=False,
                 cd_player=False, leather_seats=False, sunroof=False, gps_navigation=False,
                 backup_camera=False):
        
        self.__id = car_id
        self.__title = title
        self.__brand_name = brand_name
        self.__model_name = model_name
        self.__year = year
        self.__price = price
        self.__mileage = mileage
        self.__fuel_type = fuel_type
        self.__transmission = transmission
        self.__engine_size = engine_size
        self.__power = power
        self.__doors = doors
        self.__seats = seats
        self.__color = color
        self.__condition = condition
        self.__description = description
        self.__location = location
        self.__city = city
        self.__district = district
        self.__postal_code = postal_code
        self.__status = status
        self.__is_featured = is_featured
        self.__seller_id = seller_id
        self.__images = images or []
        
        # Equipamentos
        self.__air_conditioning = air_conditioning
        self.__power_steering = power_steering
        self.__electric_windows = electric_windows
        self.__airbags = airbags
        self.__abs_brakes = abs_brakes
        self.__alarm_system = alarm_system
        self.__alloy_wheels = alloy_wheels
        self.__cd_player = cd_player
        self.__leather_seats = leather_seats
        self.__sunroof = sunroof
        self.__gps_navigation = gps_navigation
        self.__backup_camera = backup_camera
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, car_id):
        self.__id = car_id
    
    @property
    def title(self):
        return self.__title
    
    @title.setter
    def title(self, title):
        self.__title = title.strip() if title else ""
    
    @property
    def brand_name(self):
        return self.__brand_name
    
    @brand_name.setter
    def brand_name(self, brand_name):
        self.__brand_name = brand_name.strip() if brand_name else ""
    
    @property
    def model_name(self):
        return self.__model_name
    
    @model_name.setter
    def model_name(self, model_name):
        self.__model_name = model_name.strip() if model_name else ""
    
    @property
    def year(self):
        return self.__year
    
    @year.setter
    def year(self, year):
        self.__year = int(year) if year else 0
    
    @property
    def price(self):
        return self.__price
    
    @price.setter
    def price(self, price):
        self.__price = Decimal(str(price)) if price else Decimal('0.00')
    
    @property
    def mileage(self):
        return self.__mileage
    
    @mileage.setter
    def mileage(self, mileage):
        self.__mileage = int(mileage) if mileage else 0
    
    @property
    def fuel_type(self):
        return self.__fuel_type
    
    @fuel_type.setter
    def fuel_type(self, fuel_type):
        valid_types = ['gasoline', 'diesel', 'hybrid', 'electric', 'lpg', 'other']
        if fuel_type in valid_types:
            self.__fuel_type = fuel_type
        else:
            self.__fuel_type = 'gasoline'
    
    @property
    def transmission(self):
        return self.__transmission
    
    @transmission.setter
    def transmission(self, transmission):
        valid_types = ['manual', 'automatic', 'semi_automatic']
        if transmission in valid_types:
            self.__transmission = transmission
        else:
            self.__transmission = 'manual'
    
    @property
    def engine_size(self):
        return self.__engine_size
    
    @engine_size.setter
    def engine_size(self, engine_size):
        self.__engine_size = engine_size.strip() if engine_size else ""
    
    @property
    def power(self):
        return self.__power
    
    @power.setter
    def power(self, power):
        self.__power = int(power) if power else 0
    
    @property
    def doors(self):
        return self.__doors
    
    @doors.setter
    def doors(self, doors):
        self.__doors = int(doors) if doors else 4
    
    @property
    def seats(self):
        return self.__seats
    
    @seats.setter
    def seats(self, seats):
        self.__seats = int(seats) if seats else 5
    
    @property
    def color(self):
        return self.__color
    
    @color.setter
    def color(self, color):
        self.__color = color.strip() if color else ""
    
    @property
    def condition(self):
        return self.__condition
    
    @condition.setter
    def condition(self, condition):
        valid_conditions = ['new', 'used', 'certified']
        if condition in valid_conditions:
            self.__condition = condition
        else:
            self.__condition = 'used'
    
    @property
    def description(self):
        return self.__description
    
    @description.setter
    def description(self, description):
        self.__description = description.strip() if description else ""
    
    @property
    def location(self):
        return self.__location
    
    @location.setter
    def location(self, location):
        self.__location = location.strip() if location else ""
    
    @property
    def city(self):
        return self.__city
    
    @city.setter
    def city(self, city):
        self.__city = city.strip() if city else ""
    
    @property
    def district(self):
        return self.__district
    
    @district.setter
    def district(self, district):
        self.__district = district.strip() if district else ""
    
    @property
    def postal_code(self):
        return self.__postal_code
    
    @postal_code.setter
    def postal_code(self, postal_code):
        self.__postal_code = postal_code.strip() if postal_code else ""
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, status):
        valid_statuses = ['active', 'sold', 'reserved', 'inactive']
        if status in valid_statuses:
            self.__status = status
        else:
            self.__status = 'active'
    
    @property
    def is_featured(self):
        return self.__is_featured
    
    @is_featured.setter
    def is_featured(self, is_featured):
        self.__is_featured = bool(is_featured)
    
    @property
    def seller_id(self):
        return self.__seller_id
    
    @seller_id.setter
    def seller_id(self, seller_id):
        self.__seller_id = seller_id
    
    @property
    def images(self):
        return self.__images
    
    @images.setter
    def images(self, images):
        self.__images = images or []
    
    # Equipamentos
    @property
    def air_conditioning(self):
        return self.__air_conditioning
    
    @air_conditioning.setter
    def air_conditioning(self, air_conditioning):
        self.__air_conditioning = bool(air_conditioning)
    
    @property
    def power_steering(self):
        return self.__power_steering
    
    @power_steering.setter
    def power_steering(self, power_steering):
        self.__power_steering = bool(power_steering)
    
    @property
    def electric_windows(self):
        return self.__electric_windows
    
    @electric_windows.setter
    def electric_windows(self, electric_windows):
        self.__electric_windows = bool(electric_windows)
    
    @property
    def airbags(self):
        return self.__airbags
    
    @airbags.setter
    def airbags(self, airbags):
        self.__airbags = bool(airbags)
    
    @property
    def abs_brakes(self):
        return self.__abs_brakes
    
    @abs_brakes.setter
    def abs_brakes(self, abs_brakes):
        self.__abs_brakes = bool(abs_brakes)
    
    @property
    def alarm_system(self):
        return self.__alarm_system
    
    @alarm_system.setter
    def alarm_system(self, alarm_system):
        self.__alarm_system = bool(alarm_system)
    
    @property
    def alloy_wheels(self):
        return self.__alloy_wheels
    
    @alloy_wheels.setter
    def alloy_wheels(self, alloy_wheels):
        self.__alloy_wheels = bool(alloy_wheels)
    
    @property
    def cd_player(self):
        return self.__cd_player
    
    @cd_player.setter
    def cd_player(self, cd_player):
        self.__cd_player = bool(cd_player)
    
    @property
    def leather_seats(self):
        return self.__leather_seats
    
    @leather_seats.setter
    def leather_seats(self, leather_seats):
        self.__leather_seats = bool(leather_seats)
    
    @property
    def sunroof(self):
        return self.__sunroof
    
    @sunroof.setter
    def sunroof(self, sunroof):
        self.__sunroof = bool(sunroof)
    
    @property
    def gps_navigation(self):
        return self.__gps_navigation
    
    @gps_navigation.setter
    def gps_navigation(self, gps_navigation):
        self.__gps_navigation = bool(gps_navigation)
    
    @property
    def backup_camera(self):
        return self.__backup_camera
    
    @backup_camera.setter
    def backup_camera(self, backup_camera):
        self.__backup_camera = bool(backup_camera)
    
    def get_price_formatted(self):
        """Retorna o preço formatado"""
        return f"€{self.__price:,.2f}".replace(",", " ")
    
    def get_year_range(self):
        """Retorna o intervalo de anos"""
        current_year = 2024
        age = current_year - self.__year
        return f"{self.__year} ({age} anos)"
    
    def has_images(self):
        """Verifica se o carro tem imagens"""
        return len(self.__images) > 0


class CarSearchFilters:
    """Entidade para filtros de pesquisa de carros"""
    
    def __init__(self, search_term="", brand_id=None, model_id=None, min_price=None,
                 max_price=None, min_year=None, max_year=None, fuel_type="",
                 transmission="", min_mileage=None, max_mileage=None, city="", status="active"):
        
        self.__search_term = search_term
        self.__brand_id = brand_id
        self.__model_id = model_id
        self.__min_price = min_price
        self.__max_price = max_price
        self.__min_year = min_year
        self.__max_year = max_year
        self.__fuel_type = fuel_type
        self.__transmission = transmission
        self.__min_mileage = min_mileage
        self.__max_mileage = max_mileage
        self.__city = city
        self.__status = status
    
    @property
    def search_term(self):
        return self.__search_term
    
    @search_term.setter
    def search_term(self, search_term):
        self.__search_term = search_term.strip() if search_term else ""
    
    @property
    def brand_id(self):
        return self.__brand_id
    
    @brand_id.setter
    def brand_id(self, brand_id):
        self.__brand_id = brand_id
    
    @property
    def model_id(self):
        return self.__model_id
    
    @model_id.setter
    def model_id(self, model_id):
        self.__model_id = model_id
    
    @property
    def min_price(self):
        return self.__min_price
    
    @min_price.setter
    def min_price(self, min_price):
        self.__min_price = Decimal(str(min_price)) if min_price else None
    
    @property
    def max_price(self):
        return self.__max_price
    
    @max_price.setter
    def max_price(self, max_price):
        self.__max_price = Decimal(str(max_price)) if max_price else None
    
    @property
    def min_year(self):
        return self.__min_year
    
    @min_year.setter
    def min_year(self, min_year):
        self.__min_year = int(min_year) if min_year else None
    
    @property
    def max_year(self):
        return self.__max_year
    
    @max_year.setter
    def max_year(self, max_year):
        self.__max_year = int(max_year) if max_year else None
    
    @property
    def fuel_type(self):
        return self.__fuel_type
    
    @fuel_type.setter
    def fuel_type(self, fuel_type):
        self.__fuel_type = fuel_type
    
    @property
    def transmission(self):
        return self.__transmission
    
    @transmission.setter
    def transmission(self, transmission):
        self.__transmission = transmission
    
    @property
    def min_mileage(self):
        return self.__min_mileage
    
    @min_mileage.setter
    def min_mileage(self, min_mileage):
        self.__min_mileage = int(min_mileage) if min_mileage else None
    
    @property
    def max_mileage(self):
        return self.__max_mileage
    
    @max_mileage.setter
    def max_mileage(self, max_mileage):
        self.__max_mileage = int(max_mileage) if max_mileage else None
    
    @property
    def city(self):
        return self.__city
    
    @city.setter
    def city(self, city):
        self.__city = city.strip() if city else ""
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, status):
        self.__status = status 