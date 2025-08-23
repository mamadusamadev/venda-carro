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


# Registar modelos de compra
from .models_purchase import PurchaseRequest, Purchase, PurchaseStatusHistory, Notification


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('buyer_name', 'car', 'seller', 'status', 'proposed_price', 'created_at')
    list_filter = ('status', 'created_at', 'seller')
    search_fields = ('buyer_name', 'buyer_email', 'car__title', 'seller__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('car', 'buyer', 'seller', 'status')
        }),
        ('Dados do Comprador', {
            'fields': ('buyer_name', 'buyer_email', 'buyer_phone', 'buyer_address', 'buyer_city', 'buyer_postal_code')
        }),
        ('Proposta', {
            'fields': ('proposed_price', 'message')
        }),
        ('Resposta do Vendedor', {
            'fields': ('seller_response', 'seller_responded_at')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('buyer_name', 'car', 'seller', 'purchase_price', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'seller')
    search_fields = ('buyer_name', 'buyer_email', 'car__title', 'seller__username', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'payment_confirmed_at', 'delivered_at', 'completed_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('car', 'buyer', 'seller', 'purchase_price')
        }),
        ('Dados do Comprador', {
            'fields': ('buyer_name', 'buyer_email', 'buyer_phone', 'buyer_address', 'buyer_city', 'buyer_postal_code')
        }),
        ('Status', {
            'fields': ('status', 'payment_status')
        }),
        ('Pagamento', {
            'fields': ('payment_method', 'transaction_id', 'payment_confirmed_at')
        }),
        ('Entrega', {
            'fields': ('tracking_code', 'delivered_at')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PurchaseStatusHistory)
class PurchaseStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'previous_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('previous_status', 'new_status', 'created_at')
    search_fields = ('purchase__buyer_name', 'purchase__car__title', 'changed_by__username')
    readonly_fields = ('created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'type', 'title', 'message')
        }),
        ('Referências', {
            'fields': ('purchase_request', 'purchase', 'car'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at', 'read_at')
        })
    )


# Registar modelos de chat
from .models_chat import ChatRoom, ChatMessage, ChatNotification


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('car', 'buyer', 'seller', 'status', 'created_at', 'last_activity')
    list_filter = ('status', 'created_at', 'last_activity')
    search_fields = ('car__title', 'buyer__username', 'seller__username')
    readonly_fields = ('created_at', 'last_activity')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('car', 'buyer', 'seller', 'status')
        }),
        ('Controle', {
            'fields': ('closed_by', 'closed_at', 'buyer_last_read', 'seller_last_read')
        }),
        ('Datas', {
            'fields': ('created_at', 'last_activity'),
            'classes': ('collapse',)
        })
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'sender', 'message_type', 'content_preview', 'created_at', 'is_deleted')
    list_filter = ('message_type', 'is_deleted', 'created_at')
    search_fields = ('content', 'sender__username', 'chat_room__car__title')
    readonly_fields = ('created_at', 'edited_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Conteúdo'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('chat_room', 'sender', 'message_type')
        }),
        ('Conteúdo', {
            'fields': ('content', 'attachment', 'attachment_name')
        }),
        ('Status', {
            'fields': ('is_edited', 'is_deleted', 'created_at', 'edited_at')
        })
    )


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'content', 'recipient__username')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('recipient', 'chat_room', 'message', 'notification_type')
        }),
        ('Conteúdo', {
            'fields': ('title', 'content')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at', 'read_at')
        })
    )