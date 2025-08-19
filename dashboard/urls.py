from django.urls import path
from . import views
from . import views_new

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    
    # Gestão de carros (versões antigas)
    path('carros/', views.car_list, name='car_list'),
    path('carros/<uuid:car_id>/', views.car_detail, name='car_detail'),
    path('carros/adicionar/', views.car_add, name='car_add'),
    path('carros/<uuid:car_id>/editar/', views.car_edit, name='car_edit'),
    path('carros/<uuid:car_id>/eliminar/', views.car_delete, name='car_delete'),
    
    # Gestão de carros (novas versões com arquitetura melhorada)
    path('carros/novo/adicionar/', views_new.car_add_new, name='car_add_new'),
    path('carros/novo/<uuid:car_id>/editar/', views_new.car_edit_new, name='car_edit_new'),
    path('carros/novo/lista/', views_new.car_list_new, name='car_list_new'),
    
    # Carros do utilizador
    path('meus-carros/', views.my_cars, name='my_cars'),
    path('meus-carros/novo/', views_new.my_cars_new, name='my_cars_new'),
    
    # Funcionalidades AJAX
    path('favoritos/<uuid:car_id>/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('api/modelos/', views.get_car_models, name='get_car_models'),
    path('api/modelos/novo/', views_new.get_car_models_ajax, name='get_car_models_new'),
    path('api/imagens/<int:image_id>/eliminar/', views_new.delete_car_image, name='delete_car_image'),
    
    # Estatísticas
    path('estatisticas/', views.statistics, name='statistics'),
] 