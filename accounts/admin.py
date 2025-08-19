from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, SellerProfile, BuyerProfile, UserVerification

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para o modelo User
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_premium', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_premium', 'email_verified', 'phone_verified', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informações Pessoais'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'birth_date', 'avatar')
        }),
        (_('Tipo e Localização'), {
            'fields': ('user_type', 'city', 'district')
        }),
        (_('Verificações'), {
            'fields': ('is_verified', 'is_premium', 'email_verified', 'phone_verified')
        }),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas Importantes'), {
            'fields': ('last_login', 'date_joined')
        }),
        (_('Metadados'), {
            'fields': ('last_login_ip', 'login_count'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )


class SellerProfileInline(admin.StackedInline):
    """
    Inline para SellerProfile
    """
    model = SellerProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Vendedor'
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('seller_type', 'company_name', 'nif')
        }),
        (_('Morada'), {
            'fields': ('address', 'city', 'district', 'postal_code')
        }),
        (_('Informações Comerciais'), {
            'fields': ('description', 'business_hours', 'website')
        }),
        (_('Redes Sociais'), {
            'fields': ('facebook_url', 'instagram_url', 'linkedin_url'),
            'classes': ('collapse',)
        }),
        (_('Estatísticas'), {
            'fields': ('rating', 'total_sales', 'total_reviews'),
            'classes': ('collapse',)
        }),
        (_('Configurações'), {
            'fields': ('auto_renew_ads', 'allow_phone_contact', 'allow_email_contact'),
            'classes': ('collapse',)
        }),
    )


class BuyerProfileInline(admin.StackedInline):
    """
    Inline para BuyerProfile
    """
    model = BuyerProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Comprador'
    
    fieldsets = (
        (_('Preferências de Compra'), {
            'fields': ('preferred_brands', 'min_budget', 'max_budget', 'preferred_fuel_type')
        }),
        (_('Filtros'), {
            'fields': ('min_year', 'max_year', 'max_mileage')
        }),
        (_('Histórico'), {
            'fields': ('total_purchases', 'total_spent'),
            'classes': ('collapse',)
        }),
        (_('Notificações'), {
            'fields': ('email_notifications', 'sms_notifications', 'push_notifications'),
            'classes': ('collapse',)
        }),
        (_('Alertas'), {
            'fields': ('price_alert_enabled', 'new_cars_alert'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    """
    Admin para SellerProfile
    """
    list_display = ('user', 'seller_type', 'company_name', 'city', 'rating', 'total_sales', 'created_at')
    list_filter = ('seller_type', 'city', 'district', 'rating', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'nif')
    readonly_fields = ('rating', 'total_sales', 'total_reviews', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Utilizador'), {
            'fields': ('user',)
        }),
        (_('Informações Básicas'), {
            'fields': ('seller_type', 'company_name', 'nif')
        }),
        (_('Morada'), {
            'fields': ('address', 'city', 'district', 'postal_code')
        }),
        (_('Informações Comerciais'), {
            'fields': ('description', 'business_hours', 'website')
        }),
        (_('Redes Sociais'), {
            'fields': ('facebook_url', 'instagram_url', 'linkedin_url')
        }),
        (_('Estatísticas'), {
            'fields': ('rating', 'total_sales', 'total_reviews')
        }),
        (_('Configurações'), {
            'fields': ('auto_renew_ads', 'allow_phone_contact', 'allow_email_contact')
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    """
    Admin para BuyerProfile
    """
    list_display = ('user', 'preferred_fuel_type', 'max_budget', 'total_purchases', 'created_at')
    list_filter = ('preferred_fuel_type', 'email_notifications', 'sms_notifications', 'created_at')
    search_fields = ('user__username', 'user__email', 'preferred_brands')
    readonly_fields = ('total_purchases', 'total_spent', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Utilizador'), {
            'fields': ('user',)
        }),
        (_('Preferências de Compra'), {
            'fields': ('preferred_brands', 'min_budget', 'max_budget', 'preferred_fuel_type')
        }),
        (_('Filtros'), {
            'fields': ('min_year', 'max_year', 'max_mileage')
        }),
        (_('Histórico'), {
            'fields': ('total_purchases', 'total_spent')
        }),
        (_('Notificações'), {
            'fields': ('email_notifications', 'sms_notifications', 'push_notifications')
        }),
        (_('Alertas'), {
            'fields': ('price_alert_enabled', 'new_cars_alert')
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    """
    Admin para UserVerification
    """
    list_display = ('user', 'verification_type', 'status', 'verified_by', 'created_at')
    list_filter = ('verification_type', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'verification_code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Verificação'), {
            'fields': ('user', 'verification_type', 'status')
        }),
        (_('Documentação'), {
            'fields': ('document', 'verification_code', 'notes')
        }),
        (_('Aprovação'), {
            'fields': ('verified_by', 'expires_at')
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'verified_by')
