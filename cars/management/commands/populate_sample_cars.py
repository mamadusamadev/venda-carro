from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cars.models import Brand, CarModel, Car
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Popula a base de dados com carros de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Número de carros a criar (padrão: 20)',
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'A criar {count} carros de exemplo...')
        
        # Obter ou criar utilizador vendedor
        admin_user, created = User.objects.get_or_create(
            username='vendedor_exemplo',
            defaults={
                'email': 'vendedor@carzone.pt',
                'first_name': 'João',
                'last_name': 'Silva',
                'user_type': 'seller',
                'is_verified': True,
                'city': 'Lisboa',
                'district': 'Lisboa'
            }
        )
        
        if created:
            admin_user.set_password('password123')
            admin_user.save()
            self.stdout.write('✓ Utilizador vendedor criado')

        # Dados de exemplo para carros
        sample_cars = [
            {
                'brand': 'Toyota', 'model': 'Corolla', 'version': '1.6 VVT-i',
                'year': 2020, 'color': 'Branco Pérola', 'fuel': 'gasoline',
                'transmission': 'manual', 'mileage': 45000, 'price': 18500,
                'city': 'Lisboa', 'district': 'Lisboa'
            },
            {
                'brand': 'BMW', 'model': 'Série 3', 'version': '320d xDrive',
                'year': 2019, 'color': 'Preto Metálico', 'fuel': 'diesel',
                'transmission': 'automatic', 'mileage': 62000, 'price': 32000,
                'city': 'Porto', 'district': 'Porto'
            },
            {
                'brand': 'Mercedes-Benz', 'model': 'Classe C', 'version': 'C200 AMG Line',
                'year': 2021, 'color': 'Cinzento Selenite', 'fuel': 'gasoline',
                'transmission': 'automatic', 'mileage': 28000, 'price': 42000,
                'city': 'Braga', 'district': 'Braga'
            },
            {
                'brand': 'Volkswagen', 'model': 'Golf', 'version': '1.5 TSI',
                'year': 2020, 'color': 'Azul Atlântico', 'fuel': 'gasoline',
                'transmission': 'manual', 'mileage': 38000, 'price': 22000,
                'city': 'Coimbra', 'district': 'Coimbra'
            },
            {
                'brand': 'Audi', 'model': 'A4', 'version': '2.0 TDI S-Line',
                'year': 2018, 'color': 'Branco Ibis', 'fuel': 'diesel',
                'transmission': 'automatic', 'mileage': 75000, 'price': 28500,
                'city': 'Faro', 'district': 'Faro'
            },
            {
                'brand': 'Ford', 'model': 'Focus', 'version': '1.0 EcoBoost',
                'year': 2019, 'color': 'Vermelho Race', 'fuel': 'gasoline',
                'transmission': 'manual', 'mileage': 52000, 'price': 16800,
                'city': 'Aveiro', 'district': 'Aveiro'
            },
            {
                'brand': 'Renault', 'model': 'Clio', 'version': '1.2 TCe',
                'year': 2021, 'color': 'Branco Glaciar', 'fuel': 'gasoline',
                'transmission': 'manual', 'mileage': 15000, 'price': 14500,
                'city': 'Setúbal', 'district': 'Setúbal'
            },
            {
                'brand': 'Peugeot', 'model': '308', 'version': '1.6 BlueHDi',
                'year': 2020, 'color': 'Cinzento Artense', 'fuel': 'diesel',
                'transmission': 'manual', 'mileage': 41000, 'price': 17900,
                'city': 'Viseu', 'district': 'Viseu'
            },
            {
                'brand': 'Opel', 'model': 'Astra', 'version': '1.4 Turbo',
                'year': 2019, 'color': 'Preto Absoluto', 'fuel': 'gasoline',
                'transmission': 'automatic', 'mileage': 48000, 'price': 16200,
                'city': 'Leiria', 'district': 'Leiria'
            },
            {
                'brand': 'Seat', 'model': 'Leon', 'version': '1.5 TSI FR',
                'year': 2021, 'color': 'Laranja Nevada', 'fuel': 'gasoline',
                'transmission': 'manual', 'mileage': 22000, 'price': 21500,
                'city': 'Santarém', 'district': 'Santarém'
            }
        ]

        # Descrições de exemplo
        descriptions = [
            "Carro em excelente estado de conservação, sempre bem cuidado. Revisões em dia, pneus novos. Ideal para família.",
            "Veículo impecável, único dono, sempre na garagem. Extras incluídos: GPS, sensores, câmara traseira.",
            "Automóvel muito bem estimado, sem acidentes. Manutenção sempre feita na marca. Documentação em ordem.",
            "Carro como novo, poucos quilómetros, ainda com garantia. Equipamento completo, ar condicionado, bluetooth.",
            "Excelente oportunidade! Carro em perfeitas condições, motor irrepreensível. Aceito retoma.",
            "Veículo de família, muito bem cuidado. Histórico completo de manutenção. Pronto a andar.",
            "Carro económico e fiável, perfeito para cidade. Consumos reduzidos, fácil estacionamento.",
            "Automóvel desportivo em óptimo estado. Jantes em liga, sistema de som premium, bancos em pele."
        ]

        created_cars = 0
        
        for i in range(min(count, len(sample_cars))):
            car_data = sample_cars[i]
            
            try:
                # Obter marca e modelo
                brand = Brand.objects.get(name=car_data['brand'])
                car_model = CarModel.objects.get(brand=brand, name=car_data['model'])
                
                # Criar carro
                car = Car.objects.create(
                    seller=admin_user,
                    brand=brand,
                    car_model=car_model,
                    version=car_data['version'],
                    year=car_data['year'],
                    color=car_data['color'],
                    fuel_type=car_data['fuel'],
                    transmission=car_data['transmission'],
                    engine_size=Decimal(str(random.uniform(1.0, 3.0))),
                    power=random.randint(90, 250),
                    mileage=car_data['mileage'],
                    doors=random.choice([3, 4, 5]),
                    seats=random.choice([4, 5, 7]),
                    condition='used',
                    license_plate=f"{random.randint(10,99)}-{random.choice(['AB','CD','EF','GH'])}-{random.randint(10,99)}",
                    price=Decimal(str(car_data['price'])),
                    negotiable=random.choice([True, False]),
                    city=car_data['city'],
                    district=car_data['district'],
                    postal_code=f"{random.randint(1000,9999)}-{random.randint(100,999)}",
                    title=f"{brand.name} {car_model.name} {car_data['version']} - {car_data['year']}",
                    description=random.choice(descriptions),
                    
                    # Equipamentos aleatórios
                    air_conditioning=random.choice([True, False]),
                    gps=random.choice([True, False]),
                    bluetooth=random.choice([True, False]),
                    parking_sensors=random.choice([True, False]),
                    backup_camera=random.choice([True, False]),
                    leather_seats=random.choice([True, False]),
                    electric_windows=random.choice([True, False]),
                    central_locking=random.choice([True, False]),
                    abs_brakes=random.choice([True, False]),
                    airbags=random.choice([True, False]),
                    
                    status='active',
                    views=random.randint(0, 500),
                    favorites_count=random.randint(0, 25)
                )
                
                created_cars += 1
                self.stdout.write(f'✓ Carro criado: {car}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar carro {car_data["brand"]} {car_data["model"]}: {str(e)}')
                )
        
        # Se pediu mais carros do que temos dados, criar variações
        if count > len(sample_cars):
            remaining = count - len(sample_cars)
            self.stdout.write(f'A criar {remaining} carros adicionais com variações...')
            
            for i in range(remaining):
                base_car = random.choice(sample_cars)
                
                try:
                    brand = Brand.objects.get(name=base_car['brand'])
                    car_model = CarModel.objects.get(brand=brand, name=base_car['model'])
                    
                    # Criar variação
                    year_variation = random.randint(2016, 2023)
                    mileage_variation = random.randint(10000, 120000)
                    price_variation = random.randint(8000, 50000)
                    
                    car = Car.objects.create(
                        seller=admin_user,
                        brand=brand,
                        car_model=car_model,
                        version=base_car.get('version', ''),
                        year=year_variation,
                        color=random.choice(['Branco', 'Preto', 'Cinzento', 'Azul', 'Vermelho', 'Prata']),
                        fuel_type=random.choice(['gasoline', 'diesel', 'hybrid', 'electric']),
                        transmission=random.choice(['manual', 'automatic']),
                        engine_size=Decimal(str(random.uniform(1.0, 3.0))),
                        power=random.randint(90, 300),
                        mileage=mileage_variation,
                        doors=random.choice([3, 4, 5]),
                        seats=random.choice([4, 5, 7]),
                        condition=random.choice(['used', 'new', 'certified']),
                        license_plate=f"{random.randint(10,99)}-{random.choice(['AB','CD','EF','GH','IJ','KL'])}-{random.randint(10,99)}",
                        price=Decimal(str(price_variation)),
                        negotiable=random.choice([True, False]),
                        city=random.choice(['Lisboa', 'Porto', 'Braga', 'Coimbra', 'Faro', 'Aveiro', 'Setúbal']),
                        district=random.choice(['Lisboa', 'Porto', 'Braga', 'Coimbra', 'Faro', 'Aveiro', 'Setúbal']),
                        postal_code=f"{random.randint(1000,9999)}-{random.randint(100,999)}",
                        title=f"{brand.name} {car_model.name} - {year_variation}",
                        description=random.choice(descriptions),
                        
                        # Equipamentos aleatórios
                        air_conditioning=random.choice([True, False]),
                        gps=random.choice([True, False]),
                        bluetooth=random.choice([True, False]),
                        parking_sensors=random.choice([True, False]),
                        backup_camera=random.choice([True, False]),
                        leather_seats=random.choice([True, False]),
                        electric_windows=random.choice([True, False]),
                        central_locking=random.choice([True, False]),
                        abs_brakes=random.choice([True, False]),
                        airbags=random.choice([True, False]),
                        
                        status=random.choice(['active', 'active', 'active', 'sold']),  # 75% ativos
                        views=random.randint(0, 500),
                        favorites_count=random.randint(0, 25)
                    )
                    
                    created_cars += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Erro ao criar carro variação: {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Concluído! Criados {created_cars} carros de exemplo.'
            )
        ) 