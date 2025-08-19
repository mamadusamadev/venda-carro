from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime

from cars.models import Brand, CarModel


class CarForm(forms.Form):
    """Formulário para adicionar/editar carros com suporte a múltiplas imagens"""
    
    FUEL_TYPE_CHOICES = [
        ('gasoline', 'Gasolina'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Híbrido'),
        ('electric', 'Elétrico'),
        ('lpg', 'GPL'),
        ('other', 'Outro')
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automática'),
        ('semi_automatic', 'Semi-automática')
    ]
    
    CONDITION_CHOICES = [
        ('new', 'Novo'),
        ('used', 'Usado'),
        ('certified', 'Certificado')
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('sold', 'Vendido'),
        ('reserved', 'Reservado'),
        ('inactive', 'Inativo')
    ]
    
    DOORS_CHOICES = [
        (2, '2 portas'),
        (3, '3 portas'),
        (4, '4 portas'),
        (5, '5 portas')
    ]
    
    SEATS_CHOICES = [
        (2, '2 lugares'),
        (4, '4 lugares'),
        (5, '5 lugares'),
        (7, '7 lugares'),
        (8, '8 lugares'),
        (9, '9 lugares')
    ]
    
    # === INFORMAÇÕES BÁSICAS ===
    title = forms.CharField(
        label="Título do Anúncio",
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: BMW Série 3 320d em excelente estado',
            'required': True
        })
    )
    
    brand = forms.ModelChoiceField(
        label="Marca",
        queryset=Brand.objects.filter(is_active=True).order_by('name'),
        empty_label="Selecione uma marca",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
            'id': 'id_brand'
        })
    )
    
    car_model = forms.ModelChoiceField(
        label="Modelo",
        queryset=CarModel.objects.none(),  # Será preenchido via AJAX
        empty_label="Selecione primeiro uma marca",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
            'id': 'id_car_model'
        })
    )
    
    year = forms.IntegerField(
        label="Ano",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 2020',
            'min': 1990,
            'max': datetime.now().year + 1,
            'required': True
        })
    )
    
    price = forms.DecimalField(
        label="Preço (€)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 25000.00',
            'step': '0.01',
            'min': '0',
            'required': True
        })
    )
    
    mileage = forms.IntegerField(
        label="Quilometragem (km)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 50000',
            'min': '0',
            'required': True
        })
    )
    
    condition = forms.ChoiceField(
        label="Estado",
        choices=CONDITION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    # === ESPECIFICAÇÕES TÉCNICAS ===
    fuel_type = forms.ChoiceField(
        label="Tipo de Combustível",
        choices=FUEL_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    transmission = forms.ChoiceField(
        label="Transmissão",
        choices=TRANSMISSION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    engine_size = forms.CharField(
        label="Cilindrada",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 2.0L, 1600cc'
        })
    )
    
    power = forms.IntegerField(
        label="Potência (CV)",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 150',
            'min': '0'
        })
    )
    
    doors = forms.ChoiceField(
        label="Número de Portas",
        choices=DOORS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    seats = forms.ChoiceField(
        label="Número de Lugares",
        choices=SEATS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    color = forms.CharField(
        label="Cor",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Preto, Branco, Prata'
        })
    )
    
    # === LOCALIZAÇÃO ===
    location = forms.CharField(
        label="Localização",
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Rua das Flores, 123'
        })
    )
    
    city = forms.CharField(
        label="Cidade",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Lisboa',
            'required': True
        })
    )
    
    district = forms.CharField(
        label="Distrito",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Lisboa'
        })
    )
    
    postal_code = forms.CharField(
        label="Código Postal",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 1000-001'
        })
    )
    
    # === DESCRIÇÃO ===
    description = forms.CharField(
        label="Descrição",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Descreva o carro em detalhe...',
            'rows': 5
        })
    )
    
    # === IMAGENS (Temporário - será implementado upload múltiplo depois) ===
    # Por agora, vamos usar um campo simples de arquivo
    main_image = forms.ImageField(
        label="Imagem Principal",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Selecione a imagem principal do carro (JPG, PNG, máx. 5MB)"
    )
    
    # === EQUIPAMENTOS ===
    air_conditioning = forms.BooleanField(
        label="Ar Condicionado",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    power_steering = forms.BooleanField(
        label="Direção Assistida",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    electric_windows = forms.BooleanField(
        label="Vidros Elétricos",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    airbags = forms.BooleanField(
        label="Airbags",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    abs_brakes = forms.BooleanField(
        label="ABS",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    alarm_system = forms.BooleanField(
        label="Sistema de Alarme",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    alloy_wheels = forms.BooleanField(
        label="Jantes de Liga",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    cd_player = forms.BooleanField(
        label="Leitor CD/MP3",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    leather_seats = forms.BooleanField(
        label="Bancos em Pele",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    sunroof = forms.BooleanField(
        label="Teto de Abrir",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    gps_navigation = forms.BooleanField(
        label="GPS/Navegação",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    backup_camera = forms.BooleanField(
        label="Câmara de Marcha-atrás",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # === STATUS ===
    status = forms.ChoiceField(
        label="Estado do Anúncio",
        choices=STATUS_CHOICES,
        initial='active',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_featured = forms.BooleanField(
        label="Anúncio em Destaque",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Anúncios em destaque aparecem primeiro nos resultados"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se há dados de uma marca selecionada, carrega os modelos
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['car_model'].queryset = CarModel.objects.filter(
                    brand_id=brand_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.initial.get('brand'):
            self.fields['car_model'].queryset = CarModel.objects.filter(
                brand=self.initial['brand'], is_active=True
            ).order_by('name')
    

    
    def clean_year(self):
        """Valida o ano"""
        year = self.cleaned_data.get('year')
        current_year = datetime.now().year
        
        if year and (year < 1990 or year > current_year + 1):
            raise ValidationError(f"Ano deve estar entre 1990 e {current_year + 1}.")
        
        return year
    
    def clean_price(self):
        """Valida o preço"""
        price = self.cleaned_data.get('price')
        
        if price and price <= 0:
            raise ValidationError("O preço deve ser maior que zero.")
        
        if price and price > Decimal('999999.99'):
            raise ValidationError("Preço muito alto.")
        
        return price
    
    def clean_mileage(self):
        """Valida a quilometragem"""
        mileage = self.cleaned_data.get('mileage')
        
        if mileage and mileage < 0:
            raise ValidationError("A quilometragem não pode ser negativa.")
        
        if mileage and mileage > 1000000:
            raise ValidationError("Quilometragem muito alta.")
        
        return mileage


class CarSearchForm(forms.Form):
    """Formulário de pesquisa de carros"""
    
    search = forms.CharField(
        label="Pesquisar",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pesquisar por título, marca, modelo...'
        })
    )
    
    brand = forms.ModelChoiceField(
        label="Marca",
        queryset=Brand.objects.filter(is_active=True).order_by('name'),
        empty_label="Todas as marcas",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        label="Preço Mínimo",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'step': '100'
        })
    )
    
    max_price = forms.DecimalField(
        label="Preço Máximo",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '100000',
            'step': '100'
        })
    )
    
    min_year = forms.IntegerField(
        label="Ano Mínimo",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2000'
        })
    )
    
    max_year = forms.IntegerField(
        label="Ano Máximo",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': str(datetime.now().year)
        })
    )
    
    fuel_type = forms.ChoiceField(
        label="Combustível",
        choices=[('', 'Todos')] + CarForm.FUEL_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    transmission = forms.ChoiceField(
        label="Transmissão",
        choices=[('', 'Todas')] + CarForm.TRANSMISSION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    city = forms.CharField(
        label="Cidade",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cidade'
        })
    ) 