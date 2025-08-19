from django.core.management.base import BaseCommand
from cars.models import Brand, CarModel

class Command(BaseCommand):
    help = 'Popula a base de dados com marcas e modelos de carros populares'

    def handle(self, *args, **options):
        self.stdout.write('A criar marcas e modelos de carros...')
        
        # Dados das marcas e modelos
        brands_data = {
            'Toyota': {
                'country': 'Japão',
                'models': [
                    {'name': 'Corolla', 'body_type': 'sedan', 'start_year': 1966},
                    {'name': 'Camry', 'body_type': 'sedan', 'start_year': 1982},
                    {'name': 'RAV4', 'body_type': 'suv', 'start_year': 1994},
                    {'name': 'Prius', 'body_type': 'hatchback', 'start_year': 1997},
                    {'name': 'Yaris', 'body_type': 'hatchback', 'start_year': 1999},
                    {'name': 'Hilux', 'body_type': 'pickup', 'start_year': 1968},
                ]
            },
            'BMW': {
                'country': 'Alemanha',
                'models': [
                    {'name': 'Série 3', 'body_type': 'sedan', 'start_year': 1975},
                    {'name': 'Série 5', 'body_type': 'sedan', 'start_year': 1972},
                    {'name': 'X3', 'body_type': 'suv', 'start_year': 2003},
                    {'name': 'X5', 'body_type': 'suv', 'start_year': 1999},
                    {'name': 'i3', 'body_type': 'hatchback', 'start_year': 2013},
                ]
            },
            'Mercedes-Benz': {
                'country': 'Alemanha',
                'models': [
                    {'name': 'Classe C', 'body_type': 'sedan', 'start_year': 1993},
                    {'name': 'Classe E', 'body_type': 'sedan', 'start_year': 1953},
                    {'name': 'GLA', 'body_type': 'suv', 'start_year': 2013},
                    {'name': 'GLC', 'body_type': 'suv', 'start_year': 2015},
                    {'name': 'Classe A', 'body_type': 'hatchback', 'start_year': 1997},
                ]
            },
            'Volkswagen': {
                'country': 'Alemanha',
                'models': [
                    {'name': 'Golf', 'body_type': 'hatchback', 'start_year': 1974},
                    {'name': 'Passat', 'body_type': 'sedan', 'start_year': 1973},
                    {'name': 'Polo', 'body_type': 'hatchback', 'start_year': 1975},
                    {'name': 'Tiguan', 'body_type': 'suv', 'start_year': 2007},
                    {'name': 'T-Cross', 'body_type': 'suv', 'start_year': 2018},
                ]
            },
            'Audi': {
                'country': 'Alemanha',
                'models': [
                    {'name': 'A3', 'body_type': 'hatchback', 'start_year': 1996},
                    {'name': 'A4', 'body_type': 'sedan', 'start_year': 1994},
                    {'name': 'A6', 'body_type': 'sedan', 'start_year': 1994},
                    {'name': 'Q3', 'body_type': 'suv', 'start_year': 2011},
                    {'name': 'Q5', 'body_type': 'suv', 'start_year': 2008},
                ]
            },
            'Ford': {
                'country': 'Estados Unidos',
                'models': [
                    {'name': 'Focus', 'body_type': 'hatchback', 'start_year': 1998},
                    {'name': 'Fiesta', 'body_type': 'hatchback', 'start_year': 1976},
                    {'name': 'Mondeo', 'body_type': 'sedan', 'start_year': 1993},
                    {'name': 'Kuga', 'body_type': 'suv', 'start_year': 2008},
                    {'name': 'EcoSport', 'body_type': 'suv', 'start_year': 2003},
                ]
            },
            'Renault': {
                'country': 'França',
                'models': [
                    {'name': 'Clio', 'body_type': 'hatchback', 'start_year': 1990},
                    {'name': 'Megane', 'body_type': 'hatchback', 'start_year': 1995},
                    {'name': 'Captur', 'body_type': 'suv', 'start_year': 2013},
                    {'name': 'Kadjar', 'body_type': 'suv', 'start_year': 2015},
                    {'name': 'Talisman', 'body_type': 'sedan', 'start_year': 2015},
                ]
            },
            'Peugeot': {
                'country': 'França',
                'models': [
                    {'name': '208', 'body_type': 'hatchback', 'start_year': 2012},
                    {'name': '308', 'body_type': 'hatchback', 'start_year': 2007},
                    {'name': '3008', 'body_type': 'suv', 'start_year': 2008},
                    {'name': '5008', 'body_type': 'suv', 'start_year': 2009},
                    {'name': '508', 'body_type': 'sedan', 'start_year': 2010},
                ]
            },
            'Opel': {
                'country': 'Alemanha',
                'models': [
                    {'name': 'Corsa', 'body_type': 'hatchback', 'start_year': 1982},
                    {'name': 'Astra', 'body_type': 'hatchback', 'start_year': 1991},
                    {'name': 'Insignia', 'body_type': 'sedan', 'start_year': 2008},
                    {'name': 'Crossland', 'body_type': 'suv', 'start_year': 2017},
                    {'name': 'Grandland', 'body_type': 'suv', 'start_year': 2017},
                ]
            },
            'Seat': {
                'country': 'Espanha',
                'models': [
                    {'name': 'Ibiza', 'body_type': 'hatchback', 'start_year': 1984},
                    {'name': 'Leon', 'body_type': 'hatchback', 'start_year': 1999},
                    {'name': 'Arona', 'body_type': 'suv', 'start_year': 2017},
                    {'name': 'Ateca', 'body_type': 'suv', 'start_year': 2016},
                    {'name': 'Tarraco', 'body_type': 'suv', 'start_year': 2018},
                ]
            },
        }

        created_brands = 0
        created_models = 0

        for brand_name, brand_info in brands_data.items():
            # Criar ou obter a marca
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={
                    'country': brand_info['country'],
                    'is_active': True
                }
            )
            
            if created:
                created_brands += 1
                self.stdout.write(f'✓ Marca criada: {brand_name}')
            
            # Criar modelos para a marca
            for model_info in brand_info['models']:
                car_model, model_created = CarModel.objects.get_or_create(
                    brand=brand,
                    name=model_info['name'],
                    defaults={
                        'body_type': model_info['body_type'],
                        'start_year': model_info['start_year'],
                        'is_active': True
                    }
                )
                
                if model_created:
                    created_models += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Concluído! Criadas {created_brands} marcas e {created_models} modelos.'
            )
        ) 