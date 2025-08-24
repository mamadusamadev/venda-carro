from django.urls import path
from . import views
from . import views_purchase
from . import profile_views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    
    # Gestão de carros
    path('carros/', views.car_list, name='car_list'),
    path('carros/<uuid:car_id>/', views.car_detail, name='car_detail'),
    path('carros/adicionar/', views.car_add, name='car_add'),
    path('carros/<uuid:car_id>/editar/', views.car_edit, name='car_edit'),
    path('carros/<uuid:car_id>/eliminar/', views.car_delete, name='car_delete'),
    
    # Carros do utilizador
    path('meus-carros/', views.my_cars, name='my_cars'),
    path('favoritos/', views.my_favorites, name='my_favorites'),
    
    # Funcionalidades AJAX
    path('favoritos/<uuid:car_id>/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('api/modelos/', views.get_car_models, name='get_car_models'),
    
    # Estatísticas
    path('estatisticas/', views.statistics, name='statistics'),
    
    # Alterar status do carro
    path('carros/<uuid:car_id>/alterar-status/', views.change_car_status, name='change_car_status'),
    
    # Sistema de compras
    path('carros/<uuid:car_id>/solicitar-compra/', views_purchase.purchase_request_create, name='purchase_request_create'),
    path('carros/<uuid:car_id>/comprar/', views_purchase.purchase_create, name='purchase_create'),
    path('solicitacoes/<uuid:request_id>/', views_purchase.purchase_request_detail, name='purchase_request_detail'),
    path('compras/<uuid:purchase_id>/', views_purchase.purchase_detail, name='purchase_detail'),
    path('compras/<uuid:purchase_id>/alterar-status/', views_purchase.purchase_status_update, name='purchase_status_update'),
    
    # Gestão de compras e vendas
    path('minhas-compras/', views_purchase.my_purchases, name='my_purchases'),
    path('minhas-vendas/', views_purchase.my_sales, name='my_sales'),
    
    # Notificações
    path('notificacoes/', views_purchase.notifications_list, name='notifications'),
    path('notificacoes/<uuid:notification_id>/ler/', views_purchase.notification_mark_read, name='notification_mark_read'),
    path('notificacoes/marcar-todas-lidas/', views_purchase.notifications_mark_all_read, name='notifications_mark_all_read'),
    path('notificacoes/count/', views_purchase.notifications_count, name='notifications_count'),
    
    # Perfil e Configurações
    path('perfil/', profile_views.profile_view, name='profile'),
    path('perfil/editar/', profile_views.edit_profile, name='edit_profile'),
    path('perfil/vendedor/', profile_views.edit_seller_profile, name='edit_seller_profile'),
    path('perfil/comprador/', profile_views.edit_buyer_profile, name='edit_buyer_profile'),
    path('perfil/alterar-password/', profile_views.change_password, name='change_password'),
    path('perfil/estatisticas/', profile_views.profile_statistics, name='profile_statistics'),
    path('perfil/avatar/eliminar/', profile_views.delete_avatar, name='delete_avatar'),
    path('configuracoes/', profile_views.configurations, name='configurations'),
] 