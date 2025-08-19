from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

class User(AbstractUser):
    """
    Modelo de utilizador customizado que estende o AbstractUser do Django
    """
    USER_TYPES = (
        ('buyer', 'Comprador'),
        ('seller', 'Vendedor'),
        ('both', 'Comprador e Vendedor'),
        ('admin', 'Administrador'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPES, 
        default='buyer',
        verbose_name='Tipo de Utilizador'
    )
    
    # Informações pessoais
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Número de telefone deve estar no formato: '+999999999'. Até 15 dígitos permitidos."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
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
        upload_to='avatars/%Y/%m/%d/', 
        blank=True, 
        null=True,
        verbose_name='Foto de Perfil'
    )
    
    # Status e verificações
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Utilizador Verificado'
    )
    
    is_premium = models.BooleanField(
        default=False,
        verbose_name='Utilizador Premium'
    )
    
    email_verified = models.BooleanField(
        default=False,
        verbose_name='Email Verificado'
    )
    
    phone_verified = models.BooleanField(
        default=False,
        verbose_name='Telefone Verificado'
    )
    
    # Localização
    city = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Cidade'
    )
    
    district = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Distrito'
    )
    
    # Metadados
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    login_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['city', 'district']),
        ]

    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

    def can_sell(self):
        """Verifica se o utilizador pode vender carros"""
        return self.user_type in ['seller', 'both', 'admin']

    def can_buy(self):
        """Verifica se o utilizador pode comprar carros"""
        return self.user_type in ['buyer', 'both', 'admin']
    
    def get_full_name_or_username(self):
        """Retorna nome completo ou username se nome não disponível"""
        full_name = self.get_full_name()
        return full_name if full_name else self.username
    
    def is_seller(self):
        """Verifica se o utilizador é vendedor (compatibilidade)"""
        return self.can_sell()
    
    def is_buyer(self):
        """Verifica se o utilizador é comprador (compatibilidade)"""
        return self.can_buy()


class SellerProfile(models.Model):
    """
    Perfil específico para vendedores com informações comerciais
    """
    SELLER_TYPES = (
        ('individual', 'Pessoa Singular'),
        ('dealer', 'Stand/Concessionário'),
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
    
    # Informações da empresa/stand
    company_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='Nome da Empresa/Stand'
    )
    
    nif = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name='NIF',
        help_text='Número de Identificação Fiscal'
    )
    
    # Morada comercial
    address = models.CharField(
        max_length=200,
        verbose_name='Morada Comercial'
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name='Cidade'
    )
    
    district = models.CharField(
        max_length=50,
        verbose_name='Distrito'
    )
    
    postal_code_regex = RegexValidator(
        regex=r'^\d{4}-\d{3}$',
        message='Código postal deve estar no formato: 0000-000'
    )
    postal_code = models.CharField(
        validators=[postal_code_regex],
        max_length=8,
        verbose_name='Código Postal'
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
        verbose_name='Descrição da Empresa'
    )
    
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name='Website'
    )
    
    # Redes sociais
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    # Estatísticas e avaliações
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Avaliação Média'
    )
    
    total_sales = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Vendas'
    )
    
    total_reviews = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Avaliações'
    )
    
    # Configurações de conta
    auto_renew_ads = models.BooleanField(
        default=False,
        verbose_name='Renovar Anúncios Automaticamente'
    )
    
    allow_phone_contact = models.BooleanField(
        default=True,
        verbose_name='Permitir Contacto Telefónico'
    )
    
    allow_email_contact = models.BooleanField(
        default=True,
        verbose_name='Permitir Contacto por Email'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil do Vendedor'
        verbose_name_plural = 'Perfis dos Vendedores'
        indexes = [
            models.Index(fields=['seller_type']),
            models.Index(fields=['city', 'district']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        if self.company_name:
            return f"{self.company_name} - {self.user.username}"
        return f"{self.user.get_full_name_or_username()}"
    
    def update_rating(self):
        """Atualiza a avaliação média baseada nas reviews"""
        from cars.models import Review
        reviews = Review.objects.filter(seller=self.user)
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.rating = round(avg_rating, 2)
            self.total_reviews = reviews.count()
            self.save(update_fields=['rating', 'total_reviews'])


class BuyerProfile(models.Model):
    """
    Perfil específico para compradores
    """
    FUEL_PREFERENCES = (
        ('gasoline', 'Gasolina'),
        ('diesel', 'Gasóleo'),
        ('electric', 'Elétrico'),
        ('hybrid', 'Híbrido'),
        ('lpg', 'GPL'),
        ('no_preference', 'Sem Preferência'),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='buyer_profile'
    )
    
    # Preferências de compra
    preferred_brands = models.TextField(
        blank=True,
        null=True,
        verbose_name='Marcas Preferidas',
        help_text='Separar por vírgula'
    )
    
    min_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Orçamento Mínimo (€)'
    )
    
    max_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Orçamento Máximo (€)'
    )
    
    preferred_fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_PREFERENCES,
        default='no_preference',
        verbose_name='Combustível Preferido'
    )
    
    max_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Ano Máximo'
    )
    
    min_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Ano Mínimo'
    )
    
    max_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Quilometragem Máxima'
    )
    
    # Histórico de compras
    total_purchases = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Compras'
    )
    
    total_spent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Gasto (€)'
    )
    
    # Configurações de notificações
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificações por Email'
    )
    
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name='Notificações por SMS'
    )
    
    push_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificações Push'
    )
    
    # Alertas personalizados
    price_alert_enabled = models.BooleanField(
        default=False,
        verbose_name='Alertas de Preço'
    )
    
    new_cars_alert = models.BooleanField(
        default=True,
        verbose_name='Alertas de Carros Novos'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil do Comprador'
        verbose_name_plural = 'Perfis dos Compradores'
        indexes = [
            models.Index(fields=['preferred_fuel_type']),
            models.Index(fields=['max_budget']),
        ]

    def __str__(self):
        return f"Comprador: {self.user.get_full_name_or_username()}"
    
    def get_budget_range(self):
        """Retorna o range de orçamento formatado"""
        if self.min_budget and self.max_budget:
            return f"€{self.min_budget:,.2f} - €{self.max_budget:,.2f}"
        elif self.max_budget:
            return f"Até €{self.max_budget:,.2f}"
        elif self.min_budget:
            return f"A partir de €{self.min_budget:,.2f}"
        return "Orçamento não definido"


class UserVerification(models.Model):
    """
    Modelo para gerir verificações de utilizadores
    """
    VERIFICATION_TYPES = (
        ('email', 'Verificação de Email'),
        ('phone', 'Verificação de Telefone'),
        ('identity', 'Verificação de Identidade'),
        ('address', 'Verificação de Morada'),
        ('business', 'Verificação Comercial'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('expired', 'Expirado'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    
    verification_type = models.CharField(
        max_length=20,
        choices=VERIFICATION_TYPES
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    document = models.FileField(
        upload_to='verifications/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Documento'
    )
    
    verification_code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='verified_users'
    )
    
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Verificação de Utilizador'
        verbose_name_plural = 'Verificações de Utilizadores'
        unique_together = ['user', 'verification_type']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['verification_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_verification_type_display()} ({self.get_status_display()})"
