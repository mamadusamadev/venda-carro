from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Brand, CarModel, Car, CarPhoto, Favorite, Review, 
    Message, CarComparison, PriceHistory, CarAlert
)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Admin para Brand
    """
    list_display = ('name', 'country', 'is_active', 'total_models', 'created_at')
    list_filter = ('country', 'is_active', 'created_at')
    search_fields = ('name', 'country')
    readonly_fields = ('created_at', 'updated_at')
    
    def total_models(self, obj):
        return obj.models.count()
    total_models.short_description = 'Total de Modelos'


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    """
    Admin para CarModel
    """
    list_display = ('brand', 'name', 'body_type', 'generation', 'start_year', 'end_year', 'is_active')
    list_filter = ('brand', 'body_type', 'is_active', 'start_year')
    search_fields = ('name', 'brand__name', 'generation')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('brand', 'name', 'body_type')
        }),
        (_('Geração e Anos'), {
            'fields': ('generation', 'start_year', 'end_year')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


class CarPhotoInline(admin.TabularInline):
    """
    Inline para fotos dos carros
    """
    model = CarPhoto
    extra = 1
    fields = ('photo', 'caption', 'is_main', 'order')
    readonly_fields = ('photo_preview',)
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" height="75" />', obj.photo.url)
        return "Sem foto"
    photo_preview.short_description = 'Preview'


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    """
    Admin para Car
    """
    list_display = (
        'title', 'brand', 'car_model', 'year', 'price', 'mileage', 
        'fuel_type', 'status', 'featured', 'views', 'created_at'
    )
    list_filter = (
        'status', 'featured', 'brand', 'fuel_type', 'transmission', 
        'condition', 'year', 'city', 'created_at'
    )
    search_fields = ('title', 'brand__name', 'car_model__name', 'license_plate', 'seller__username')
    readonly_fields = ('id', 'views', 'favorites_count', 'created_at', 'updated_at')
    inlines = [CarPhotoInline]
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('seller', 'title', 'brand', 'car_model', 'version', 'year', 'color')
        }),
        (_('Especificações Técnicas'), {
            'fields': ('fuel_type', 'transmission', 'engine_size', 'power', 'mileage', 'doors', 'seats')
        }),
        (_('Estado e Documentação'), {
            'fields': ('condition', 'license_plate', 'registration_date', 'inspection_valid_until', 'insurance_valid_until')
        }),
        (_('Preço'), {
            'fields': ('price', 'original_price', 'negotiable')
        }),
        (_('Localização'), {
            'fields': ('city', 'district', 'postal_code')
        }),
        (_('Descrição'), {
            'fields': ('description',)
        }),
        (_('Equipamentos'), {
            'fields': (
                'air_conditioning', 'gps', 'bluetooth', 'parking_sensors', 'backup_camera',
                'leather_seats', 'electric_windows', 'central_locking', 'abs_brakes', 'airbags'
            ),
            'classes': ('collapse',)
        }),
        (_('Status do Anúncio'), {
            'fields': ('status', 'featured', 'published_at', 'expires_at', 'sold_at')
        }),
        (_('Estatísticas'), {
            'fields': ('views', 'favorites_count')
        }),
        (_('Metadados'), {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('brand', 'car_model', 'seller')


@admin.register(CarPhoto)
class CarPhotoAdmin(admin.ModelAdmin):
    """
    Admin para CarPhoto
    """
    list_display = ('car', 'caption', 'is_main', 'order', 'photo_preview', 'created_at')
    list_filter = ('is_main', 'created_at')
    search_fields = ('car__title', 'caption')
    readonly_fields = ('photo_preview', 'created_at')
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" height="75" />', obj.photo.url)
        return "Sem foto"
    photo_preview.short_description = 'Preview'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Admin para Favorite
    """
    list_display = ('user', 'car', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'car__title', 'car__brand__name')
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin para Review
    """
    list_display = ('reviewer', 'seller', 'car', 'rating', 'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('reviewer__username', 'seller__username', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Avaliação'), {
            'fields': ('reviewer', 'seller', 'car', 'rating')
        }),
        (_('Conteúdo'), {
            'fields': ('title', 'comment')
        }),
        (_('Status'), {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin para Message
    """
    list_display = ('sender', 'recipient', 'car', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'car__title')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        (_('Participantes'), {
            'fields': ('sender', 'recipient', 'car')
        }),
        (_('Mensagem'), {
            'fields': ('subject', 'message')
        }),
        (_('Status'), {
            'fields': ('is_read', 'read_at')
        }),
        (_('Datas'), {
            'fields': ('created_at',)
        }),
    )


@admin.register(CarComparison)
class CarComparisonAdmin(admin.ModelAdmin):
    """
    Admin para CarComparison
    """
    list_display = ('user', 'name', 'total_cars', 'created_at')
    search_fields = ('user__username', 'name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('cars',)
    
    def total_cars(self, obj):
        return obj.cars.count()
    total_cars.short_description = 'Total de Carros'


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    """
    Admin para PriceHistory
    """
    list_display = ('car', 'old_price', 'new_price', 'price_change', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('car__title', 'car__brand__name')
    readonly_fields = ('created_at',)
    
    def price_change(self, obj):
        change = obj.get_price_change_percentage()
        color = 'green' if change > 0 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, change
        )
    price_change.short_description = 'Variação (%)'


@admin.register(CarAlert)
class CarAlertAdmin(admin.ModelAdmin):
    """
    Admin para CarAlert
    """
    list_display = ('user', 'name', 'is_active', 'email_notifications', 'last_notification', 'created_at')
    list_filter = ('is_active', 'email_notifications', 'created_at')
    search_fields = ('user__username', 'name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('brands', 'car_models')
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('user', 'name', 'is_active')
        }),
        (_('Critérios de Pesquisa'), {
            'fields': ('brands', 'car_models', 'min_price', 'max_price', 'min_year', 'max_year')
        }),
        (_('Filtros Adicionais'), {
            'fields': ('fuel_types', 'max_mileage', 'cities'),
            'classes': ('collapse',)
        }),
        (_('Notificações'), {
            'fields': ('email_notifications', 'last_notification')
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
