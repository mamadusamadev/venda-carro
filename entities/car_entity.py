from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from django.core.files.uploadedfile import UploadedFile


class Car:
    def __init__(self, title, description, brand, car_model, year, condition, price, 
                 original_price=None, negotiable=False, mileage=0, fuel_type='gasoline',
                 transmission='manual', engine_size=1.0, doors=4, seats=5, color='white',
                 license_plate='', registration_date=None, inspection_valid_until=None,
                 insurance_valid_until=None, city='', district='', postal_code='',
                 seller=None, status='active', featured=False, air_conditioning=False,
                 abs_brakes=False, airbags=False, backup_camera=False, bluetooth=False,
                 central_locking=False, electric_windows=False, gps=False, 
                 leather_seats=False, parking_sensors=False, power=100, version=''):
        self.__title = title
        self.__description = description
        self.__brand = brand
        self.__car_model = car_model
        self.__year = year
        self.__condition = condition
        self.__price = price
        self.__original_price = original_price
        self.__negotiable = negotiable
        self.__mileage = mileage
        self.__fuel_type = fuel_type
        self.__transmission = transmission
        self.__engine_size = engine_size
        self.__doors = doors
        self.__seats = seats
        self.__color = color
        self.__license_plate = license_plate
        self.__registration_date = registration_date
        self.__inspection_valid_until = inspection_valid_until
        self.__insurance_valid_until = insurance_valid_until
        self.__city = city
        self.__district = district
        self.__postal_code = postal_code
        self.__seller = seller
        self.__status = status
        self.__featured = featured
        self.__air_conditioning = air_conditioning
        self.__abs_brakes = abs_brakes
        self.__airbags = airbags
        self.__backup_camera = backup_camera
        self.__bluetooth = bluetooth
        self.__central_locking = central_locking
        self.__electric_windows = electric_windows
        self.__gps = gps
        self.__leather_seats = leather_seats
        self.__parking_sensors = parking_sensors
        self.__power = power
        self.__version = version

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description

    @property
    def brand(self):
        return self.__brand

    @brand.setter
    def brand(self, brand):
        self.__brand = brand

    @property
    def car_model(self):
        return self.__car_model

    @car_model.setter
    def car_model(self, car_model):
        self.__car_model = car_model

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, year):
        self.__year = year

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition):
        self.__condition = condition

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        self.__price = price

    @property
    def original_price(self):
        return self.__original_price

    @original_price.setter
    def original_price(self, original_price):
        self.__original_price = original_price

    @property
    def negotiable(self):
        return self.__negotiable

    @negotiable.setter
    def negotiable(self, negotiable):
        self.__negotiable = negotiable

    @property
    def mileage(self):
        return self.__mileage

    @mileage.setter
    def mileage(self, mileage):
        self.__mileage = mileage

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
    def engine_size(self):
        return self.__engine_size

    @engine_size.setter
    def engine_size(self, engine_size):
        self.__engine_size = engine_size

    @property
    def doors(self):
        return self.__doors

    @doors.setter
    def doors(self, doors):
        self.__doors = doors

    @property
    def seats(self):
        return self.__seats

    @seats.setter
    def seats(self, seats):
        self.__seats = seats

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color):
        self.__color = color

    @property
    def license_plate(self):
        return self.__license_plate

    @license_plate.setter
    def license_plate(self, license_plate):
        self.__license_plate = license_plate

    @property
    def registration_date(self):
        return self.__registration_date

    @registration_date.setter
    def registration_date(self, registration_date):
        self.__registration_date = registration_date

    @property
    def inspection_valid_until(self):
        return self.__inspection_valid_until

    @inspection_valid_until.setter
    def inspection_valid_until(self, inspection_valid_until):
        self.__inspection_valid_until = inspection_valid_until

    @property
    def insurance_valid_until(self):
        return self.__insurance_valid_until

    @insurance_valid_until.setter
    def insurance_valid_until(self, insurance_valid_until):
        self.__insurance_valid_until = insurance_valid_until

    @property
    def city(self):
        return self.__city

    @city.setter
    def city(self, city):
        self.__city = city

    @property
    def district(self):
        return self.__district

    @district.setter
    def district(self, district):
        self.__district = district

    @property
    def postal_code(self):
        return self.__postal_code

    @postal_code.setter
    def postal_code(self, postal_code):
        self.__postal_code = postal_code

    @property
    def seller(self):
        return self.__seller

    @seller.setter
    def seller(self, seller):
        self.__seller = seller

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    @property
    def featured(self):
        return self.__featured

    @featured.setter
    def featured(self, featured):
        self.__featured = featured

    @property
    def air_conditioning(self):
        return self.__air_conditioning

    @air_conditioning.setter
    def air_conditioning(self, air_conditioning):
        self.__air_conditioning = air_conditioning

    @property
    def abs_brakes(self):
        return self.__abs_brakes

    @abs_brakes.setter
    def abs_brakes(self, abs_brakes):
        self.__abs_brakes = abs_brakes

    @property
    def airbags(self):
        return self.__airbags

    @airbags.setter
    def airbags(self, airbags):
        self.__airbags = airbags

    @property
    def backup_camera(self):
        return self.__backup_camera

    @backup_camera.setter
    def backup_camera(self, backup_camera):
        self.__backup_camera = backup_camera

    @property
    def bluetooth(self):
        return self.__bluetooth

    @bluetooth.setter
    def bluetooth(self, bluetooth):
        self.__bluetooth = bluetooth

    @property
    def central_locking(self):
        return self.__central_locking

    @central_locking.setter
    def central_locking(self, central_locking):
        self.__central_locking = central_locking

    @property
    def electric_windows(self):
        return self.__electric_windows

    @electric_windows.setter
    def electric_windows(self, electric_windows):
        self.__electric_windows = electric_windows

    @property
    def gps(self):
        return self.__gps

    @gps.setter
    def gps(self, gps):
        self.__gps = gps

    @property
    def leather_seats(self):
        return self.__leather_seats

    @leather_seats.setter
    def leather_seats(self, leather_seats):
        self.__leather_seats = leather_seats

    @property
    def parking_sensors(self):
        return self.__parking_sensors

    @parking_sensors.setter
    def parking_sensors(self, parking_sensors):
        self.__parking_sensors = parking_sensors

    @property
    def power(self):
        return self.__power

    @power.setter
    def power(self, power):
        self.__power = power

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, version):
        self.__version = version


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