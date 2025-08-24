from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db import transaction

from forms.profile_forms import (
    UserProfileForm, SellerProfileForm, BuyerProfileForm, PasswordChangeForm
)
from accounts.models import SellerProfile, BuyerProfile


@login_required
def profile_view(request):
    """Página principal do perfil do utilizador"""
    
    context = {
        'user': request.user,
        'user_type': request.user.user_type,
        'is_seller': request.user.can_sell(),
        'is_buyer': request.user.can_buy(),
    }
    
    # Adicionar dados específicos do vendedor se aplicável
    if request.user.can_sell():
        try:
            seller_profile = request.user.seller_profile
            context['seller_profile'] = seller_profile
        except SellerProfile.DoesNotExist:
            context['seller_profile'] = None
    
    # Adicionar dados específicos do comprador se aplicável
    if request.user.can_buy():
        try:
            buyer_profile = request.user.buyer_profile
            context['buyer_profile'] = buyer_profile
        except BuyerProfile.DoesNotExist:
            context['buyer_profile'] = None
    
    return render(request, 'dashboard/profile/profile.html', context)


@login_required
def edit_profile(request):
    """Editar informações básicas do perfil"""
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('dashboard:profile')
            except Exception as e:
                messages.error(request, 'Erro ao atualizar perfil. Tente novamente.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'page_title': 'Editar Perfil'
    }
    
    return render(request, 'dashboard/profile/edit_profile.html', context)


@login_required
def edit_seller_profile(request):
    """Editar perfil de vendedor"""
    
    if not request.user.can_sell():
        messages.error(request, 'Não tem permissão para aceder a esta página.')
        return redirect('dashboard:profile')
    
    # Obter ou criar perfil de vendedor
    seller_profile, created = SellerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'address': '',
            'city': request.user.city or '',
            'district': request.user.district or '',
            'postal_code': '0000-000'
        }
    )
    
    if request.method == 'POST':
        form = SellerProfileForm(request.POST, instance=seller_profile)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, 'Perfil de vendedor atualizado com sucesso!')
                    return redirect('dashboard:profile')
            except Exception as e:
                messages.error(request, 'Erro ao atualizar perfil. Tente novamente.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = SellerProfileForm(instance=seller_profile)
    
    context = {
        'form': form,
        'seller_profile': seller_profile,
        'page_title': 'Perfil de Vendedor'
    }
    
    return render(request, 'dashboard/profile/edit_seller_profile.html', context)


@login_required
def edit_buyer_profile(request):
    """Editar perfil de comprador"""
    
    if not request.user.can_buy():
        messages.error(request, 'Não tem permissão para aceder a esta página.')
        return redirect('dashboard:profile')
    
    # Obter ou criar perfil de comprador
    buyer_profile, created = BuyerProfile.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        form = BuyerProfileForm(request.POST, instance=buyer_profile)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, 'Preferências atualizadas com sucesso!')
                    return redirect('dashboard:profile')
            except Exception as e:
                messages.error(request, 'Erro ao atualizar preferências. Tente novamente.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = BuyerProfileForm(instance=buyer_profile)
    
    context = {
        'form': form,
        'buyer_profile': buyer_profile,
        'page_title': 'Preferências de Compra'
    }
    
    return render(request, 'dashboard/profile/edit_buyer_profile.html', context)


@login_required
def change_password(request):
    """Alterar palavra-passe"""
    
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            try:
                # Alterar palavra-passe
                new_password = form.cleaned_data['new_password']
                request.user.set_password(new_password)
                request.user.save()
                
                # Manter utilizador logado
                update_session_auth_hash(request, request.user)
                
                messages.success(request, 'Palavra-passe alterada com sucesso!')
                return redirect('dashboard:profile')
            except Exception as e:
                messages.error(request, 'Erro ao alterar palavra-passe. Tente novamente.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': 'Alterar Palavra-passe'
    }
    
    return render(request, 'dashboard/profile/change_password.html', context)


@login_required
def configurations(request):
    """Página de configurações gerais"""
    
    if request.method == 'POST':
        # Processar configurações específicas via AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            action = request.POST.get('action')
            
            if action == 'toggle_notifications':
                notification_type = request.POST.get('type')
                enabled = request.POST.get('enabled') == 'true'
                
                try:
                    if request.user.can_buy():
                        buyer_profile, created = BuyerProfile.objects.get_or_create(
                            user=request.user
                        )
                        
                        if notification_type == 'email':
                            buyer_profile.notifications_email = enabled
                        elif notification_type == 'sms':
                            buyer_profile.notifications_sms = enabled
                        elif notification_type == 'push':
                            buyer_profile.notifications_push = enabled
                        elif notification_type == 'price_alerts':
                            buyer_profile.price_alerts = enabled
                        elif notification_type == 'new_car_alerts':
                            buyer_profile.new_car_alerts = enabled
                        
                        buyer_profile.save()
                    
                    return JsonResponse({
                        'success': True, 
                        'message': 'Configuração atualizada!'
                    })
                except Exception as e:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Erro ao atualizar configuração.'
                    })
            
            elif action == 'delete_account':
                # Implementação futura para eliminação de conta
                return JsonResponse({
                    'success': False, 
                    'message': 'Funcionalidade em desenvolvimento.'
                })
    
    # Obter configurações atuais
    context = {
        'user': request.user,
        'page_title': 'Configurações'
    }
    
    if request.user.can_buy():
        try:
            buyer_profile = request.user.buyer_profile
            context['buyer_profile'] = buyer_profile
        except BuyerProfile.DoesNotExist:
            context['buyer_profile'] = None
    
    return render(request, 'dashboard/profile/configurations.html', context)


@login_required
def profile_statistics(request):
    """Estatísticas do perfil do utilizador"""
    
    from cars.models import Car, CarView, CarFavorite
    from django.db.models import Count, Avg, Q
    from datetime import datetime, timedelta
    
    stats = {}
    
    # Estatísticas para vendedores
    if request.user.can_sell():
        user_cars = Car.objects.filter(seller=request.user)
        
        stats['seller'] = {
            'total_cars': user_cars.count(),
            'active_cars': user_cars.filter(status='available').count(),
            'sold_cars': user_cars.filter(status='sold').count(),
            'total_views': CarView.objects.filter(car__seller=request.user).count(),
            'total_favorites': CarFavorite.objects.filter(car__seller=request.user).count(),
            'average_price': user_cars.aggregate(avg_price=Avg('price'))['avg_price'] or 0,
        }
        
        # Views nos últimos 30 dias
        last_30_days = datetime.now() - timedelta(days=30)
        stats['seller']['views_last_30_days'] = CarView.objects.filter(
            car__seller=request.user,
            viewed_at__gte=last_30_days
        ).count()
    
    # Estatísticas para compradores
    if request.user.can_buy():
        stats['buyer'] = {
            'total_favorites': CarFavorite.objects.filter(user=request.user).count(),
            'total_views': CarView.objects.filter(user=request.user).count(),
            'searches_last_30_days': CarView.objects.filter(
                user=request.user,
                viewed_at__gte=datetime.now() - timedelta(days=30)
            ).count(),
        }
    
    context = {
        'stats': stats,
        'page_title': 'Estatísticas'
    }
    
    return render(request, 'dashboard/profile/statistics.html', context)


@login_required
def delete_avatar(request):
    """Eliminar avatar do utilizador"""
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            if request.user.avatar:
                request.user.avatar.delete()
                request.user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Avatar eliminado com sucesso!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Nenhum avatar para eliminar.'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao eliminar avatar.'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})
