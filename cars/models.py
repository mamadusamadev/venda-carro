from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class Brand(models.Model):
    """
    Modelo para marcas de carros
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='Marca')
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name='Logótipo')
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name='País de Origem')
    website = models.URLField(blank=True, null=True, verbose_name='Website Oficial')
    is_active = models.BooleanField(default=True, verbose_name='Ativa')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['name']

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """
    Modelo para modelos de carros
    """
    BODY_TYPES = (
        ('sedan', 'Sedan'),
        ('hatchback', 'Hatchback'),
        ('suv', 'SUV'),
        ('coupe', 'Coupé'),
        ('convertible', 'Conversível'),
        ('wagon', 'Carrinha'),
        ('pickup', 'Pick-up'),
        ('van', 'Carrinha de Carga'),
        ('minivan', 'Monovolume'),
    )
    
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100, verbose_name='Modelo')
    body_type = models.CharField(max_length=20, choices=BODY_TYPES, verbose_name='Tipo de Carroçaria')
    generation = models.CharField(max_length=50, blank=True, null=True, verbose_name='Geração')
    start_year = models.PositiveIntegerField(verbose_name='Ano de Início')
    end_year = models.PositiveIntegerField(blank=True, null=True, verbose_name='Ano de Fim')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Modelo de Carro'
        verbose_name_plural = 'Modelos de Carros'
        unique_together = ['brand', 'name', 'generation']
        ordering = ['brand__name', 'name']

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Car(models.Model):
    """
    Modelo principal para carros
    """
    STATUS_CHOICES = (
        ('active', 'Ativo'),
        ('sold', 'Vendido'),
        ('reserved', 'Reservado'),
        ('inactive', 'Inativo'),
        ('pending', 'Pendente Aprovação'),
        ('rejected', 'Rejeitado'),
    )
    
    FUEL_CHOICES = (
        ('gasoline', 'Gasolina'),
        ('diesel', 'Gasóleo'),
        ('electric', 'Elétrico'),
        ('hybrid', 'Híbrido'),
        ('plugin_hybrid', 'Híbrido Plug-in'),
        ('lpg', 'GPL'),
        ('ethanol', 'Etanol'),
    )
    
    TRANSMISSION_CHOICES = (
        ('manual', 'Manual'),
        ('automatic', 'Automático'),
        ('semi_automatic', 'Semi-automático'),
        ('cvt', 'CVT'),
    )
    
    CONDITION_CHOICES = (
        ('new', 'Novo'),
        ('used', 'Usado'),
        ('certified', 'Seminovo Certificado'),
        ('damaged', 'Danificado'),
    )
    
    DOOR_CHOICES = (
        (2, '2 Portas'),
        (3, '3 Portas'),
        (4, '4 Portas'),
        (5, '5 Portas'),
    )
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cars_for_sale',
        limit_choices_to={'user_type__in': ['seller', 'both', 'admin']}
    )
    
    # Informações básicas
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Marca')
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name='Modelo')
    version = models.CharField(max_length=100, blank=True, null=True, verbose_name='Versão')
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year + 1)],
        verbose_name='Ano'
    )
    color = models.CharField(max_length=50, verbose_name='Cor')
    
    # Especificações técnicas
    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_CHOICES,
        verbose_name='Combustível'
    )
    
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        verbose_name='Caixa de Velocidades'
    )
    
    engine_size = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name='Cilindrada (L)'
    )
    
    power = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Potência (CV)'
    )
    
    mileage = models.PositiveIntegerField(verbose_name='Quilometragem (km)')
    
    doors = models.PositiveSmallIntegerField(
        choices=DOOR_CHOICES,
        default=4,
        verbose_name='Número de Portas'
    )
    
    seats = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(9)],
        default=5,
        verbose_name='Número de Lugares'
    )
    
    # Estado e condição
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='used',
        verbose_name='Estado'
    )
    
    # Documentação
    license_plate = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Matrícula'
    )
    
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Matrícula'
    )
    
    inspection_valid_until = models.DateField(
        blank=True,
        null=True,
        verbose_name='IPO Válido Até'
    )
    
    insurance_valid_until = models.DateField(
        blank=True,
        null=True,
        verbose_name='Seguro Válido Até'
    )
    
    # Preço e negociação
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço (€)'
    )
    
    original_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Preço Original (€)'
    )
    
    negotiable = models.BooleanField(
        default=True,
        verbose_name='Preço Negociável'
    )
    
    # Localização
    city = models.CharField(max_length=100, verbose_name='Cidade')
    district = models.CharField(max_length=50, verbose_name='Distrito')
    postal_code = models.CharField(max_length=8, blank=True, null=True, verbose_name='Código Postal')
    
    # Descrição e características
    title = models.CharField(max_length=200, verbose_name='Título do Anúncio')
    description = models.TextField(verbose_name='Descrição')
    
    # Extras e equipamentos
    air_conditioning = models.BooleanField(default=False, verbose_name='Ar Condicionado')
    gps = models.BooleanField(default=False, verbose_name='GPS')
    bluetooth = models.BooleanField(default=False, verbose_name='Bluetooth')
    parking_sensors = models.BooleanField(default=False, verbose_name='Sensores de Estacionamento')
    backup_camera = models.BooleanField(default=False, verbose_name='Câmara de Marcha-atrás')
    leather_seats = models.BooleanField(default=False, verbose_name='Bancos em Pele')
    electric_windows = models.BooleanField(default=False, verbose_name='Vidros Elétricos')
    central_locking = models.BooleanField(default=False, verbose_name='Fecho Central')
    abs_brakes = models.BooleanField(default=False, verbose_name='ABS')
    airbags = models.BooleanField(default=False, verbose_name='Airbags')
    
    # Status e metadados
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado do Anúncio'
    )
    
    featured = models.BooleanField(default=False, verbose_name='Anúncio em Destaque')
    views = models.PositiveIntegerField(default=0, verbose_name='Visualizações')
    favorites_count = models.PositiveIntegerField(default=0, verbose_name='Número de Favoritos')
    
    # Datas importantes
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='Data de Publicação')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='Data de Expiração')
    sold_at = models.DateTimeField(blank=True, null=True, verbose_name='Data de Venda')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carro'
        verbose_name_plural = 'Carros'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['brand', 'car_model']),
            models.Index(fields=['price']),
            models.Index(fields=['year']),
            models.Index(fields=['fuel_type']),
            models.Index(fields=['city', 'district']),
            models.Index(fields=['featured', '-created_at']),
        ]

    def __str__(self):
        return f"{self.brand.name} {self.car_model.name} {self.year} - €{self.price:,.2f}"

    def is_available(self):
        return self.status == 'active'
    
    def is_expired(self):
        return self.expires_at and self.expires_at < timezone.now()
    
    def increment_views(self):
        """Incrementa o contador de visualizações"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_main_photo(self):
        """Retorna a foto principal do carro"""
        return self.photos.filter(is_main=True).first()
    
    def get_price_per_year(self):
        """Calcula preço por ano de uso"""
        age = datetime.now().year - self.year
        if age > 0:
            return self.price / age
        return self.price


class CarPhoto(models.Model):
    """
    Fotos dos carros
    """
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    
    photo = models.ImageField(
        upload_to='cars/%Y/%m/%d/',
        verbose_name='Foto'
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Legenda'
    )
    
    is_main = models.BooleanField(
        default=False,
        verbose_name='Foto Principal'
    )
    
    order = models.PositiveIntegerField(default=0, verbose_name='Ordem')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Foto do Carro'
        verbose_name_plural = 'Fotos dos Carros'

    def __str__(self):
        return f"Foto de {self.car} {'(Principal)' if self.is_main else ''}"
    
    def save(self, *args, **kwargs):
        # Garantir que apenas uma foto é principal por carro
        if self.is_main:
            CarPhoto.objects.filter(car=self.car, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class Favorite(models.Model):
    """
    Sistema de favoritos
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'car']
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} favoritou {self.car}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualizar contador de favoritos do carro
        self.car.favorites_count = self.car.favorited_by.count()
        self.car.save(update_fields=['favorites_count'])
    
    def delete(self, *args, **kwargs):
        car = self.car
        super().delete(*args, **kwargs)
        # Atualizar contador de favoritos do carro
        car.favorites_count = car.favorited_by.count()
        car.save(update_fields=['favorites_count'])


class Review(models.Model):
    """
    Avaliações de vendedores
    """
    RATING_CHOICES = (
        (1, '1 Estrela'),
        (2, '2 Estrelas'),
        (3, '3 Estrelas'),
        (4, '4 Estrelas'),
        (5, '5 Estrelas'),
    )
    
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        limit_choices_to={'user_type__in': ['seller', 'both']}
    )
    
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,
        null=True
    )
    
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name='Avaliação'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título da Avaliação'
    )
    
    comment = models.TextField(
        verbose_name='Comentário'
    )
    
    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name='Compra Verificada'
    )
    
    is_approved = models.BooleanField(
        default=True,
        verbose_name='Aprovado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ['reviewer', 'seller', 'car']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"Avaliação de {self.reviewer.username} para {self.seller.username} - {self.rating} estrelas"


class Message(models.Model):
    """
    Sistema de mensagens entre compradores e vendedores
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name='Assunto'
    )
    
    message = models.TextField(verbose_name='Mensagem')
    
    is_read = models.BooleanField(default=False, verbose_name='Lida')
    read_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['car', '-created_at']),
        ]

    def __str__(self):
        return f"Mensagem de {self.sender.username} para {self.recipient.username} sobre {self.car}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class CarComparison(models.Model):
    """
    Sistema de comparação de carros
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comparisons'
    )
    
    cars = models.ManyToManyField(
        Car,
        verbose_name='Carros para Comparar'
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nome da Comparação'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comparação'
        verbose_name_plural = 'Comparações'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comparação de {self.user.username}: {self.name}"


class PriceHistory(models.Model):
    """
    Histórico de preços dos carros
    """
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    
    old_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço Anterior (€)'
    )
    
    new_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Novo Preço (€)'
    )
    
    change_reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Motivo da Alteração'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico de Preços'
        verbose_name_plural = 'Histórico de Preços'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.car} - €{self.old_price} → €{self.new_price}"
    
    def get_price_change_percentage(self):
        """Calcula a percentagem de mudança de preço"""
        if self.old_price > 0:
            return ((self.new_price - self.old_price) / self.old_price) * 100
        return 0


class CarAlert(models.Model):
    """
    Alertas personalizados de carros
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='car_alerts'
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nome do Alerta'
    )
    
    # Critérios de pesquisa
    brands = models.ManyToManyField(
        Brand,
        blank=True,
        verbose_name='Marcas'
    )
    
    car_models = models.ManyToManyField(
        CarModel,
        blank=True,
        verbose_name='Modelos'
    )
    
    min_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Preço Mínimo (€)'
    )
    
    max_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Preço Máximo (€)'
    )
    
    min_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Ano Mínimo'
    )
    
    max_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Ano Máximo'
    )
    
    fuel_types = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Tipos de Combustível',
        help_text='Separar por vírgula'
    )
    
    max_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Quilometragem Máxima'
    )
    
    cities = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Cidades',
        help_text='Separar por vírgula'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Alerta Ativo'
    )
    
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificações por Email'
    )
    
    last_notification = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última Notificação'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Alerta de Carro'
        verbose_name_plural = 'Alertas de Carros'
        ordering = ['-created_at']

    def __str__(self):
        return f"Alerta de {self.user.username}: {self.name}"
