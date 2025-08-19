from django.urls import path
from . import views

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
    
    # Funcionalidades AJAX
    path('favoritos/<uuid:car_id>/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('api/modelos/', views.get_car_models, name='get_car_models'),
    
    # Estatísticas
    path('estatisticas/', views.statistics, name='statistics'),
    
    # Alterar status do carro
    path('carros/<uuid:car_id>/alterar-status/', views.change_car_status, name='change_car_status'),
] 