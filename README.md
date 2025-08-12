# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de usuário customizado que estende o AbstractUser do Django
    """
    USER_TYPES = (
        ('buyer', 'Comprador'),
        ('seller', 'Vendedor'),
        ('both', 'Comprador e Vendedor'),
    )
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPES, 
        default='buyer',
        verbose_name='Tipo de Usuário'
    )
    
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name='Telefone'
    )
    
    birth_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Data de Nascimento'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True,
        verbose_name='Foto de Perfil'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Usuário Verificado'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

    def can_sell(self):
        """Verifica se o usuário pode vender carros"""
        return self.user_type in ['seller', 'both']

    def can_buy(self):
        """Verifica se o usuário pode comprar carros"""
        return self.user_type in ['buyer', 'both']


class SellerProfile(models.Model):
    """
    Perfil específico para vendedores com informações adicionais
    """
    SELLER_TYPES = (
        ('individual', 'Pessoa Física'),
        ('dealer', 'Concessionária'),
        ('company', 'Empresa'),
    )
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )
    
    seller_type = models.CharField(
        max_length=15,
        choices=SELLER_TYPES,
        default='individual',
        verbose_name='Tipo de Vendedor'
    )
    
    # Para pessoa jurídica
    company_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='Nome da Empresa'
    )
    
    company_nif = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name='NIF da Empresa'
    )
    
    # Para pessoa física
    nif = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        verbose_name='NIF/Contribuinte'
    )
    
    # Endereço
    address = models.CharField(
        max_length=200,
        verbose_name='Morada'
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name='Cidade'
    )
    
    district = models.CharField(
        max_length=50,
        verbose_name='Distrito'
    )
    
    postal_code = models.CharField(
        max_length=8,
        verbose_name='Código Postal',
        help_text='Formato: 0000-000'
    )
    
    # Informações comerciais
    business_hours = models.TextField(
        blank=True,
        null=True,
        verbose_name='Horário de Funcionamento'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name='Website'
    )
    
    # Verificações e avaliações
    is_premium = models.BooleanField(
        default=False,
        verbose_name='Vendedor Premium'
    )
    
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name='Avaliação'
    )
    
    total_sales = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Vendas'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil do Vendedor'
        verbose_name_plural = 'Perfis dos Vendedores'

    def __str__(self):
        if self.company_name:
            return f"{self.company_name} - {self.user.username}"
        return f"{self.user.get_full_name()} - {self.user.username}"


class BuyerProfile(models.Model):
    """
    Perfil específico para compradores
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='buyer_profile'
    )
    
    # Preferências de compra
    preferred_brands = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Marcas Preferidas',
        help_text='Separar por vírgula'
    )
    
    max_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Orçamento Máximo'
    )
    
    preferred_fuel_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Tipo de Combustível Preferido'
    )
    
    # Histórico
    total_purchases = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Compras'
    )
    
    # Notificações
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificações por Email'
    )
    
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name='Notificações por SMS'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil do Comprador'
        verbose_name_plural = 'Perfis dos Compradores'

    def __str__(self):
        return f"Comprador: {self.user.get_full_name()} - {self.user.username}"


# Modelo para os carros (exemplo básico)
class Car(models.Model):
    """
    Modelo básico para os carros
    """
    STATUS_CHOICES = (
        ('available', 'Disponível'),
        ('sold', 'Vendido'),
        ('reserved', 'Reservado'),
        ('inactive', 'Inativo'),
    )
    
    FUEL_CHOICES = (
        ('gasoline', 'Gasolina'),
        ('ethanol', 'Etanol'),
        ('flex', 'Flex'),
        ('diesel', 'Diesel'),
        ('electric', 'Elétrico'),
        ('hybrid', 'Híbrido'),
    )
    
    TRANSMISSION_CHOICES = (
        ('manual', 'Manual'),
        ('automatic', 'Automático'),
        ('cvt', 'CVT'),
    )
    
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cars_for_sale',
        limit_choices_to={'user_type__in': ['seller', 'both']}
    )
    
    # Informações básicas
    brand = models.CharField(max_length=50, verbose_name='Marca')
    model = models.CharField(max_length=100, verbose_name='Modelo')
    year = models.PositiveIntegerField(verbose_name='Ano')
    color = models.CharField(max_length=30, verbose_name='Cor')
    
    # Especificações
    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_CHOICES,
        verbose_name='Combustível'
    )
    
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        verbose_name='Câmbio'
    )
    
    mileage = models.PositiveIntegerField(verbose_name='Quilometragem')
    engine = models.CharField(max_length=20, verbose_name='Motor')
    
    # Preço e status
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='Status'
    )
    
    # Descrição e fotos
    description = models.TextField(verbose_name='Descrição')
    main_photo = models.ImageField(
        upload_to='cars/',
        verbose_name='Foto Principal'
    )
    
    # Metadados
    views = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False, verbose_name='Destaque')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carro'
        verbose_name_plural = 'Carros'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.model} {self.year} - R$ {self.price}"

    def is_available(self):
        return self.status == 'available'


class CarPhoto(models.Model):
    """
    Fotos adicionais dos carros
    """
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    
    photo = models.ImageField(
        upload_to='cars/gallery/',
        verbose_name='Foto'
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Legenda'
    )
    
    order = models.PositiveIntegerField(default=0, verbose_name='Ordem')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Foto do Carro'
        verbose_name_plural = 'Fotos dos Carros'

    def __str__(self):
        return f"Foto de {self.car}"


# Modelo para favoritos
class Favorite(models.Model):
    """
    Sistema de favoritos para compradores
    """
    buyer = models.ForeignKey(
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
        unique_together = ['buyer', 'car']
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'

    def __str__(self):
        return f"{self.buyer.username} favoritou {self.car}"