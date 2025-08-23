from django import forms
from django.forms import Select, TextInput, Textarea, FileInput, NumberInput, CheckboxInput
from cars.models import Car, Brand, CarModel


class CarForm(forms.ModelForm):
    main_image = forms.ImageField(
        required=False,
        widget=FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'main_image'
        }),
        label='Imagem Principal'
    )
    
    class Meta:
        model = Car
        fields = [
            'title', 'brand', 'car_model', 'year', 'price', 'original_price',
            'mileage', 'fuel_type', 'transmission', 'condition', 'doors',
            'seats', 'color', 'engine_size', 'power', 'license_plate',
            'description', 'city', 'district', 'postal_code', 'negotiable',
            # Features
            'air_conditioning', 'abs_brakes', 'airbags', 'electric_windows',
            'central_locking', 'leather_seats', 'gps',
            'bluetooth', 'backup_camera', 'parking_sensors',
            # Dates
            'registration_date', 'inspection_valid_until', 'insurance_valid_until'
        ]
        
        widgets = {
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: BMW 320d Pack M'}),
            'brand': Select(attrs={'class': 'form-control'}),
            'car_model': Select(attrs={'class': 'form-control'}),
            'year': NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2025'}),
            'price': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'original_price': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'mileage': NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fuel_type': Select(attrs={'class': 'form-control'}),
            'transmission': Select(attrs={'class': 'form-control'}),
            'condition': Select(attrs={'class': 'form-control'}),
            'doors': Select(attrs={'class': 'form-control'}),
            'seats': NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '9'}),
            'color': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Azul Metálico'}),
            'engine_size': NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'power': NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'license_plate': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 00-AA-00'}),
            'description': Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Descreva as características e estado do veículo...'
            }),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Lisboa'}),
            'district': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Lisboa'}),
            'postal_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1000-001'}),
            'negotiable': CheckboxInput(attrs={'class': 'form-check-input'}),
            # Features
            'air_conditioning': CheckboxInput(attrs={'class': 'form-check-input'}),
            'abs_brakes': CheckboxInput(attrs={'class': 'form-check-input'}),
            'airbags': CheckboxInput(attrs={'class': 'form-check-input'}),
            'electric_windows': CheckboxInput(attrs={'class': 'form-check-input'}),
            'central_locking': CheckboxInput(attrs={'class': 'form-check-input'}),
            'leather_seats': CheckboxInput(attrs={'class': 'form-check-input'}),
            'gps': CheckboxInput(attrs={'class': 'form-check-input'}),
            'bluetooth': CheckboxInput(attrs={'class': 'form-check-input'}),
            'backup_camera': CheckboxInput(attrs={'class': 'form-check-input'}),
            'parking_sensors': CheckboxInput(attrs={'class': 'form-check-input'}),
            # Dates
            'registration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inspection_valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'insurance_valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
        labels = {
            'title': 'Título do Anúncio',
            'brand': 'Marca',
            'car_model': 'Modelo',
            'year': 'Ano',
            'price': 'Preço (€)',
            'original_price': 'Preço Original (€)',
            'mileage': 'Quilometragem',
            'fuel_type': 'Combustível',
            'transmission': 'Transmissão',
            'condition': 'Condição',
            'doors': 'Portas',
            'seats': 'Lugares',
            'color': 'Cor',
            'engine_size': 'Cilindrada (L)',
            'power': 'Potência (CV)',
            'license_plate': 'Matrícula',
            'description': 'Descrição',
            'city': 'Cidade',
            'district': 'Distrito',
            'postal_code': 'Código Postal',
            'negotiable': 'Preço Negociável',
            # Features
            'air_conditioning': 'Ar Condicionado',
            'abs_brakes': 'ABS',
            'airbags': 'Airbags',
            'electric_windows': 'Vidros Elétricos',
            'central_locking': 'Fecho Central',
            'leather_seats': 'Bancos em Pele',
            'gps': 'GPS',
            'bluetooth': 'Bluetooth',
            'backup_camera': 'Câmara de Marcha-atrás',
            'parking_sensors': 'Sensores de Estacionamento',
            # Dates
            'registration_date': 'Data de Matrícula',
            'inspection_valid_until': 'IPO Válido Até',
            'insurance_valid_until': 'Seguro Válido Até',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para car_model baseado na brand selecionada
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['car_model'].queryset = CarModel.objects.filter(
                    brand_id=brand_id, 
                    is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                self.fields['car_model'].queryset = CarModel.objects.none()
        elif self.instance and self.instance.pk and hasattr(self.instance, 'brand_id') and self.instance.brand_id:
            try:
                self.fields['car_model'].queryset = self.instance.brand.models.filter(is_active=True)
            except:
                self.fields['car_model'].queryset = CarModel.objects.none()
        else:
            self.fields['car_model'].queryset = CarModel.objects.none()
        
        self.fields['car_model'].empty_label = "Selecione um modelo"


class CarSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pesquisar por marca, modelo, título...'
        })
    )
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label="Todas as Marcas",
        widget=Select(attrs={
            'class': 'form-control'
        })
    )
    
    fuel_type = forms.ChoiceField(
        choices=[('', 'Combustível')] + list(Car.FUEL_CHOICES),
        required=False,
        widget=Select(attrs={
            'class': 'form-control'
        })
    )
    
    year = forms.ChoiceField(
        choices=[('', 'Ano')] + [(year, year) for year in range(2024, 1990, -1)],
        required=False,
        widget=Select(attrs={
            'class': 'form-control'
        })
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Preço Mín. €'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Preço Máx. €'
        })
    )
    
    transmission = forms.ChoiceField(
        choices=[('', 'Transmissão')] + list(Car.TRANSMISSION_CHOICES),
        required=False,
        widget=Select(attrs={
            'class': 'form-control'
        })
    )
    
    condition = forms.ChoiceField(
        choices=[('', 'Condição')] + list(Car.CONDITION_CHOICES),
        required=False,
        widget=Select(attrs={
            'class': 'form-control'
        })
    )
    
    city = forms.CharField(
        required=False,
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cidade'
        })
    )


class CarImageForm(forms.Form):
    """Formulário simplificado para upload de imagem"""
    image = forms.ImageField(
        required=False,
        widget=FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Imagem do Carro'
    ) 