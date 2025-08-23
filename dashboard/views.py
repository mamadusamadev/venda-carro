from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth

from forms.car_forms import CarForm, CarImageForm
from entities.car_entity import Car as CarEntity
from service import car_service, auth_service
from cars.models import Car, Brand, CarModel, Favorite


def is_seller_or_staff(user):
    """Verificar se o utilizador é vendedor ou staff"""
    return user.is_authenticated and (user.user_type == 'seller' or user.is_staff or user.is_superuser)


@login_required
def dashboard_home(request):
    """Página inicial do dashboard"""
    user = request.user
    
    # Estatísticas do vendedor
    if user.user_type == 'seller' or user.is_staff or user.is_superuser:
        estatisticas = car_service.obter_estatisticas_vendedor(user)
        recent_cars = car_service.listar_cars_recentes_vendedor(user, limit=6)
        
        # Dados para gráfico (últimos 6 meses)
        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_stats = Car.objects.filter(
            seller=user,
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            cars=Count('id')
        ).order_by('month')
        
        # Formatar dados para JavaScript
        monthly_data = []
        for stat in monthly_stats:
            monthly_data.append({
                'month': stat['month'].strftime('%b %Y'),
                'cars': stat['cars']
            })
        
        # Marcas mais populares (simplificado para evitar erros)
        user_cars = Car.objects.filter(seller=user)
        if user_cars.exists():
            # Obter marcas dos carros do vendedor
            brand_ids = user_cars.values_list('brand_id', flat=True).distinct()
            popular_brands = Brand.objects.filter(id__in=brand_ids)[:5]
        else:
            popular_brands = Brand.objects.filter(is_active=True)[:5]
        
        context = {
            'user': user,
            'total_cars': estatisticas['total'],
            'active_cars': estatisticas['ativos'],
            'sold_cars': estatisticas['vendidos'],
            'reserved_cars': estatisticas['reservados'],
            'total_users': auth_service.contar_users_ativos(),
            'user_cars': estatisticas['total'],
            'user_favorites': Favorite.objects.filter(user=user).count(),
            'user_messages': 0,  # Implementar quando tiver sistema de mensagens
            'recent_cars': recent_cars,
            'monthly_stats': monthly_data,
            'popular_brands': popular_brands,
        }
    else:
        # Estatísticas do comprador
        favoritos_count = Favorite.objects.filter(user=user).count()
        recent_cars = Car.objects.filter(status='active').order_by('-created_at')[:6]
        
        context = {
            'user': user,
            'total_cars': Car.objects.filter(status='active').count(),
            'active_cars': Car.objects.filter(status='active').count(),
            'sold_cars': 0,
            'reserved_cars': 0,
            'total_users': auth_service.contar_users_ativos(),
            'user_cars': 0,
            'user_favorites': favoritos_count,
            'user_messages': 0,
            'recent_cars': recent_cars,
            'monthly_stats': [],
            'popular_brands': Brand.objects.filter(is_active=True)[:5],
        }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def car_list(request):
    """Listar todos os carros - disponível para todos os utilizadores autenticados"""
    # Todos podem ver a listagem de carros
    cars = car_service.listar_cars()
    
    # Paginação
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'cars': page_obj,
        'page_obj': page_obj,
        'total_cars': cars.count(),
        'user_can_manage': is_seller_or_staff(request.user)  # Para mostrar/esconder botões de gestão
    }
    
    return render(request, 'dashboard/car_list.html', context)


@user_passes_test(is_seller_or_staff, login_url='dashboard:home')
def car_add(request):
    """Adicionar novo carro - APENAS VENDEDORES"""
    if request.method == "POST":
        form_car = CarForm(request.POST, request.FILES)
        
        if form_car.is_valid():
            # Extrair dados do formulário
            title = form_car.cleaned_data["title"]
            brand = form_car.cleaned_data["brand"]
            car_model = form_car.cleaned_data["car_model"]
            year = form_car.cleaned_data["year"]
            price = form_car.cleaned_data["price"]
            original_price = form_car.cleaned_data.get("original_price")
            mileage = form_car.cleaned_data["mileage"]
            fuel_type = form_car.cleaned_data["fuel_type"]
            transmission = form_car.cleaned_data["transmission"]
            condition = form_car.cleaned_data["condition"]
            doors = form_car.cleaned_data["doors"]
            seats = form_car.cleaned_data["seats"]
            color = form_car.cleaned_data["color"]
            engine_size = form_car.cleaned_data.get("engine_size")
            power = form_car.cleaned_data.get("power")
            description = form_car.cleaned_data["description"]
            city = form_car.cleaned_data["city"]
            district = form_car.cleaned_data["district"]
            postal_code = form_car.cleaned_data.get("postal_code")
            negotiable = form_car.cleaned_data.get("negotiable", False)
            license_plate = form_car.cleaned_data["license_plate"]
            registration_date = form_car.cleaned_data.get("registration_date")
            inspection_valid_until = form_car.cleaned_data.get("inspection_valid_until")
            insurance_valid_until = form_car.cleaned_data.get("insurance_valid_until")
            
            # Características
            air_conditioning = form_car.cleaned_data.get("air_conditioning", False)
            abs_brakes = form_car.cleaned_data.get("abs_brakes", False)
            airbags = form_car.cleaned_data.get("airbags", False)
            electric_windows = form_car.cleaned_data.get("electric_windows", False)
            central_locking = form_car.cleaned_data.get("central_locking", False)
            leather_seats = form_car.cleaned_data.get("leather_seats", False)
            gps = form_car.cleaned_data.get("gps", False)
            bluetooth = form_car.cleaned_data.get("bluetooth", False)
            backup_camera = form_car.cleaned_data.get("backup_camera", False)
            parking_sensors = form_car.cleaned_data.get("parking_sensors", False)
            
            # Criar entidade Car
            car_entity = CarEntity(
                seller=request.user,
                title=title,
                brand=brand,
                car_model=car_model,
                year=year,
                price=price,
                original_price=original_price,
                mileage=mileage,
                fuel_type=fuel_type,
                transmission=transmission,
                condition=condition,
                doors=doors,
                seats=seats,
                color=color,
                engine_size=engine_size,
                power=power,
                license_plate=license_plate,
                description=description,
                city=city,
                district=district,
                postal_code=postal_code,
                negotiable=negotiable,
                registration_date=registration_date,
                inspection_valid_until=inspection_valid_until,
                insurance_valid_until=insurance_valid_until,
                air_conditioning=air_conditioning,
                abs_brakes=abs_brakes,
                airbags=airbags,
                electric_windows=electric_windows,
                central_locking=central_locking,
                leather_seats=leather_seats,
                gps=gps,
                bluetooth=bluetooth,
                backup_camera=backup_camera,
                parking_sensors=parking_sensors,
                status='active'
            )
            
            # Cadastrar carro
            car = car_service.cadastrar_car(car_entity)
            
            if car:
                # Processar imagem principal se foi enviada
                main_image = form_car.cleaned_data.get('main_image')
                if main_image:
                    try:
                        car_service.adicionar_foto_car(car, main_image)
                    except Exception as e:
                        messages.warning(request, f'Carro adicionado, mas erro ao processar imagem: {str(e)}')
                
                messages.success(request, f'Carro "{title}" adicionado com sucesso!')
                return redirect('dashboard:my_cars')
            else:
                messages.error(request, 'Erro ao adicionar carro. Tente novamente.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form_car = CarForm()
    
    # Obter dados adicionais para o template
    from cars.models import Brand, Car
    
    context = {
        'form': form_car,
        'brands': Brand.objects.filter(is_active=True).order_by('name'),
        'years': range(datetime.now().year + 1, 1989, -1),
        'fuel_choices': Car.FUEL_CHOICES,
        'transmission_choices': Car.TRANSMISSION_CHOICES,
        'condition_choices': Car.CONDITION_CHOICES,
        'door_choices': Car.DOOR_CHOICES,
    }
    
    return render(request, 'dashboard/car_add.html', context)


@login_required
def car_detail(request, car_id):
    """Ver detalhes do carro - disponível para todos os utilizadores autenticados"""
    car = get_object_or_404(Car.objects.prefetch_related('photos'), id=car_id)
    
    # Todos podem ver detalhes de carros, mas apenas proprietários/staff podem gerir
    user_can_manage = (request.user.is_staff or car.seller == request.user) and is_seller_or_staff(request.user)
    
    # Verificar se o carro está nos favoritos do utilizador
    is_favorited = Favorite.objects.filter(user=request.user, car=car).exists()
    
    # Obter fotos do carro
    photos = car.photos.all()
    
    # Carros similares para sugestões
    similar_cars = Car.objects.filter(
        brand=car.brand,
        status='active'
    ).exclude(id=car.id).prefetch_related('photos')[:4]
    
    context = {
        'car': car,
        'photos': photos,
        'similar_cars': similar_cars,
        'user_can_manage': user_can_manage,  # Para mostrar/esconder botões de edição/eliminação
        'is_favorited': is_favorited  # Para mostrar estado do botão de favoritos
    }
    
    return render(request, 'dashboard/car_detail.html', context)


@user_passes_test(is_seller_or_staff, login_url='dashboard:home')
def car_edit(request, car_id):
    """Editar carro existente - APENAS VENDEDORES"""
    car = get_object_or_404(Car, id=car_id)
    
    # Verificar se o carro pertence ao vendedor ou se é admin
    if not request.user.is_staff and car.seller != request.user:
        messages.error(request, 'Não tem permissão para editar este carro.')
        return redirect('dashboard:my_cars')
    
    if request.method == "POST":
        form_car = CarForm(request.POST, request.FILES, instance=car)
        
        if form_car.is_valid():
            # Atualizar carro
            updated_car = form_car.save()
            
            # Processar nova imagem principal se foi enviada
            main_image = form_car.cleaned_data.get('main_image')
            if main_image:
                try:
                    car_service.adicionar_foto_car(updated_car, main_image)
                except Exception as e:
                    messages.warning(request, f'Carro atualizado, mas erro ao processar imagem: {str(e)}')
            
            messages.success(request, f'Carro "{updated_car.title}" atualizado com sucesso!')
            return redirect('dashboard:car_detail', car_id=car.id)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form_car = CarForm(instance=car)
    
    # Obter dados adicionais para o template
    from cars.models import Brand, Car
    
    context = {
        'form': form_car,
        'car': car,
        'brands': Brand.objects.filter(is_active=True).order_by('name'),
        'years': range(datetime.now().year + 1, 1989, -1),
        'fuel_choices': Car.FUEL_CHOICES,
        'transmission_choices': Car.TRANSMISSION_CHOICES,
        'condition_choices': Car.CONDITION_CHOICES,
        'door_choices': Car.DOOR_CHOICES,
    }
    
    return render(request, 'dashboard/car_edit.html', context)


@user_passes_test(is_seller_or_staff, login_url='dashboard:home')
def car_delete(request, car_id):
    """Eliminar carro - APENAS VENDEDORES"""
    car = get_object_or_404(Car, id=car_id)
    
    # Verificar se o carro pertence ao vendedor ou se é admin
    if not request.user.is_staff and car.seller != request.user:
        messages.error(request, 'Não tem permissão para eliminar este carro.')
        return redirect('dashboard:my_cars')
    
    if request.method == "POST":
        car_title = car.title
        car_service.remover_car(car)
        messages.success(request, f'Carro "{car_title}" eliminado com sucesso!')
        return redirect('dashboard:my_cars')
    
    context = {
        'car': car
    }
    
    return render(request, 'dashboard/car_confirm_delete.html', context)


@user_passes_test(is_seller_or_staff, login_url='dashboard:home')
def change_car_status(request, car_id):
    """Alterar status do carro - APENAS VENDEDORES"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    car = get_object_or_404(Car, id=car_id)
    
    # Verificar se o carro pertence ao vendedor ou se é admin
    if not request.user.is_staff and car.seller != request.user:
        return JsonResponse({'success': False, 'message': 'Não tem permissão para alterar este carro'})
    
    new_status = request.POST.get('status')
    
    if new_status not in [choice[0] for choice in Car.STATUS_CHOICES]:
        return JsonResponse({'success': False, 'message': 'Status inválido'})
    
    car.status = new_status
    car.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Status alterado para {car.get_status_display()}',
        'new_status': new_status,
        'status_display': car.get_status_display()
    })


@login_required
def my_cars(request):
    """Listar carros do vendedor logado"""
    if not is_seller_or_staff(request.user):
        messages.error(request, 'Acesso negado. Apenas vendedores podem ver esta página.')
        return redirect('dashboard:home')
    
    cars = car_service.listar_cars_vendedor(request.user)
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        cars = cars.filter(status=status_filter)
    
    # Paginação
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    estatisticas = car_service.obter_estatisticas_vendedor(request.user)
    
    context = {
        'cars': page_obj,
        'page_obj': page_obj,
        'estatisticas': estatisticas,
        'status_filter': status_filter,
        'status_choices': Car.STATUS_CHOICES
    }
    
    return render(request, 'dashboard/my_cars.html', context)


@login_required
def my_favorites(request):
    """Listar carros favoritos do utilizador"""
    # Obter favoritos do utilizador
    favorites = Favorite.objects.filter(user=request.user).select_related('car__brand', 'car__car_model', 'car__seller').order_by('-created_at')
    
    # Paginação
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'favorites': page_obj,
        'page_obj': page_obj,
        'total_favorites': favorites.count()
    }
    
    return render(request, 'dashboard/my_favorites.html', context)


@login_required
def toggle_favorite(request, car_id):
    """Toggle favorito (AJAX)"""
    if request.method == 'POST':
        car = car_service.listar_car_id(car_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            car=car
        )
        
        if not created:
            favorite.delete()
            is_favorite = False
            message = 'Removido dos favoritos'
        else:
            is_favorite = True
            message = 'Adicionado aos favoritos'
        
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'favorites_count': car.favorites_count,
            'message': message
        })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def get_car_models(request):
    """Obter modelos por marca (AJAX)"""
    brand_id = request.GET.get('brand_id')
    
    if brand_id:
        models = car_service.listar_models_por_brand(brand_id)
        models_list = [{'id': model.id, 'name': model.name} for model in models]
        return JsonResponse({'models': models_list})
    
    return JsonResponse({'models': []})


@login_required
def statistics(request):
    """Estatísticas do dashboard"""
    if request.user.is_staff:
        # Estatísticas gerais para admin
        context = {
            'total_cars': car_service.contar_cars_ativos(),
            'total_users': auth_service.contar_users_ativos(),
            'total_sellers': auth_service.contar_vendedores(),
            'total_buyers': auth_service.contar_compradores()
        }
    else:
        # Estatísticas do vendedor
        context = car_service.obter_estatisticas_vendedor(request.user)
    
    return render(request, 'dashboard/statistics.html', context)
