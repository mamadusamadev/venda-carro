from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from cars.models import Car
from cars.models_purchase import PurchaseRequest, Purchase, PurchaseStatusHistory, Notification
from forms.purchase_forms import PurchaseRequestForm, PurchaseForm, SellerResponseForm, PurchaseStatusForm


def create_notification(user, notification_type, title, message, **kwargs):
    """
    Função auxiliar para criar notificações
    """
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        purchase_request=kwargs.get('purchase_request'),
        purchase=kwargs.get('purchase'),
        car=kwargs.get('car')
    )
    return notification


def send_email_notification(user, subject, template_name, context):
    """
    Função auxiliar para enviar emails
    """
    try:
        html_message = render_to_string(template_name, context)
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erro ao enviar email: {e}")


@login_required
def purchase_request_create(request, car_id):
    """
    Criar solicitação de compra
    """
    car = get_object_or_404(Car, id=car_id)
    
    # Verificar se o utilizador não é o vendedor
    if car.seller == request.user:
        messages.error(request, 'Não pode solicitar a compra do seu próprio carro.')
        return redirect('dashboard:car_detail', car_id=car_id)
    
    # Verificar se já existe uma solicitação pendente
    existing_request = PurchaseRequest.objects.filter(
        car=car,
        buyer=request.user,
        status__in=['pending', 'negotiating', 'accepted']
    ).first()
    
    if existing_request:
        messages.warning(request, 'Já tem uma solicitação pendente para este carro.')
        return redirect('dashboard:purchase_request_detail', request_id=existing_request.id)
    
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST, user=request.user)
        
        if form.is_valid():
            purchase_request = form.save(commit=False)
            purchase_request.car = car
            purchase_request.buyer = request.user
            purchase_request.seller = car.seller
            purchase_request.save()
            
            # Criar notificação para o vendedor
            create_notification(
                user=car.seller,
                notification_type='purchase_request',
                title=f'Nova solicitação de compra para {car.title}',
                message=f'{purchase_request.buyer_name} está interessado em comprar o seu carro.',
                purchase_request=purchase_request,
                car=car
            )
            
            # Enviar email para o vendedor
            send_email_notification(
                user=car.seller,
                subject=f'Nova solicitação de compra - {car.title}',
                template_name='emails/purchase_request_notification.html',
                context={
                    'seller': car.seller,
                    'buyer': purchase_request.buyer_name,
                    'car': car,
                    'purchase_request': purchase_request,
                    'site_url': request.build_absolute_uri('/')
                }
            )
            
            messages.success(request, 'Solicitação de compra enviada com sucesso! O vendedor será notificado.')
            return redirect('dashboard:purchase_request_detail', request_id=purchase_request.id)
    else:
        form = PurchaseRequestForm(user=request.user)
    
    context = {
        'form': form,
        'car': car,
        'form_title': 'Solicitar Compra',
        'form_description': 'Preencha os seus dados e envie uma solicitação ao vendedor.'
    }
    
    return render(request, 'dashboard/purchase_request_form.html', context)


@login_required
def purchase_create(request, car_id):
    """
    Criar compra direta
    """
    car = get_object_or_404(Car, id=car_id)
    
    # Verificar se o utilizador não é o vendedor
    if car.seller == request.user:
        messages.error(request, 'Não pode comprar o seu próprio carro.')
        return redirect('dashboard:car_detail', car_id=car_id)
    
    # Verificar se o carro está disponível
    if car.status != 'active':
        messages.error(request, 'Este carro não está disponível para compra.')
        return redirect('dashboard:car_detail', car_id=car_id)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, user=request.user, car=car)
        
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.car = car
            purchase.buyer = request.user
            purchase.seller = car.seller
            purchase.purchase_price = car.price
            purchase.save()
            
            # Marcar carro como reservado
            car.status = 'reserved'
            car.save()
            
            # Criar entrada no histórico
            PurchaseStatusHistory.objects.create(
                purchase=purchase,
                previous_status='',
                new_status='pending_payment',
                changed_by=request.user,
                notes='Compra criada'
            )
            
            # Criar notificação para o vendedor
            create_notification(
                user=car.seller,
                notification_type='purchase_created',
                title=f'Nova compra para {car.title}',
                message=f'{purchase.buyer_name} comprou o seu carro por €{purchase.purchase_price}.',
                purchase=purchase,
                car=car
            )
            
            # Enviar email para o vendedor
            send_email_notification(
                user=car.seller,
                subject=f'Nova compra - {car.title}',
                template_name='emails/purchase_notification.html',
                context={
                    'seller': car.seller,
                    'buyer': purchase.buyer_name,
                    'car': car,
                    'purchase': purchase,
                    'site_url': request.build_absolute_uri('/')
                }
            )
            
            messages.success(request, 'Compra realizada com sucesso! O vendedor foi notificado e irá processar o seu pedido.')
            return redirect('dashboard:purchase_detail', purchase_id=purchase.id)
    else:
        form = PurchaseForm(user=request.user, car=car)
    
    context = {
        'form': form,
        'car': car,
        'form_title': 'Comprar Carro',
        'form_description': f'Finalizar compra de {car.title} por €{car.price}'
    }
    
    return render(request, 'dashboard/purchase_form.html', context)


@login_required
def purchase_request_detail(request, request_id):
    """
    Ver detalhes de uma solicitação de compra
    """
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    
    # Verificar se o utilizador tem permissão
    if purchase_request.buyer != request.user and purchase_request.seller != request.user:
        messages.error(request, 'Não tem permissão para ver esta solicitação.')
        return redirect('dashboard:home')
    
    # Se é o vendedor e há um POST, processar resposta
    if request.method == 'POST' and purchase_request.seller == request.user:
        form = SellerResponseForm(request.POST, instance=purchase_request)
        
        if form.is_valid():
            purchase_request = form.save(commit=False)
            purchase_request.seller_responded_at = timezone.now()
            purchase_request.save()
            
            # Criar notificação para o comprador
            status_messages = {
                'accepted': 'A sua solicitação foi aceite!',
                'rejected': 'A sua solicitação foi rejeitada.',
                'negotiating': 'O vendedor quer negociar com você.'
            }
            
            create_notification(
                user=purchase_request.buyer,
                notification_type='status_changed',
                title=f'Resposta à sua solicitação - {purchase_request.car.title}',
                message=status_messages.get(purchase_request.status, 'Status atualizado.'),
                purchase_request=purchase_request,
                car=purchase_request.car
            )
            
            messages.success(request, 'Resposta enviada com sucesso!')
            return redirect('dashboard:purchase_request_detail', request_id=request_id)
    else:
        form = SellerResponseForm(instance=purchase_request)
    
    context = {
        'purchase_request': purchase_request,
        'form': form,
        'is_seller': purchase_request.seller == request.user,
        'is_buyer': purchase_request.buyer == request.user
    }
    
    return render(request, 'dashboard/purchase_request_detail.html', context)


@login_required
def purchase_detail(request, purchase_id):
    """
    Ver detalhes de uma compra
    """
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    # Verificar se o utilizador tem permissão
    if purchase.buyer != request.user and purchase.seller != request.user:
        messages.error(request, 'Não tem permissão para ver esta compra.')
        return redirect('dashboard:home')
    
    # Obter histórico de status
    status_history = purchase.status_history.all()
    
    context = {
        'purchase': purchase,
        'status_history': status_history,
        'is_seller': purchase.seller == request.user,
        'is_buyer': purchase.buyer == request.user
    }
    
    return render(request, 'dashboard/purchase_detail.html', context)


@login_required
def purchase_status_update(request, purchase_id):
    """
    Atualizar status de uma compra (apenas vendedor)
    """
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    # Verificar se é o vendedor
    if purchase.seller != request.user:
        messages.error(request, 'Não tem permissão para alterar esta compra.')
        return redirect('dashboard:purchase_detail', purchase_id=purchase_id)
    
    if request.method == 'POST':
        form = PurchaseStatusForm(request.POST, current_status=purchase.status)
        
        if form.is_valid():
            old_status = purchase.status
            new_status = form.cleaned_data['status']
            notes = form.cleaned_data.get('notes', '')
            
            # Atualizar status
            purchase.status = new_status
            
            # Atualizar campos especiais baseados no status
            if new_status == 'payment_confirmed':
                purchase.payment_confirmed_at = timezone.now()
                purchase.payment_status = 'completed'
            elif new_status == 'delivered':
                purchase.delivered_at = timezone.now()
            elif new_status == 'completed':
                purchase.completed_at = timezone.now()
                # Marcar carro como vendido
                purchase.car.status = 'sold'
                purchase.car.save()
            
            purchase.save()
            
            # Criar entrada no histórico
            PurchaseStatusHistory.objects.create(
                purchase=purchase,
                previous_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                notes=notes
            )
            
            # Criar notificação para o comprador
            status_messages = {
                'payment_confirmed': 'O seu pagamento foi confirmado!',
                'preparing_delivery': 'O seu carro está a ser preparado para entrega.',
                'in_transit': 'O seu carro está a caminho!',
                'delivered': 'O seu carro foi entregue.',
                'completed': 'A sua compra foi concluída com sucesso!',
                'cancelled': 'A sua compra foi cancelada.'
            }
            
            create_notification(
                user=purchase.buyer,
                notification_type='status_changed',
                title=f'Status atualizado - {purchase.car.title}',
                message=status_messages.get(new_status, 'Status da compra atualizado.'),
                purchase=purchase,
                car=purchase.car
            )
            
            messages.success(request, 'Status atualizado com sucesso!')
            return redirect('dashboard:purchase_detail', purchase_id=purchase_id)
    else:
        form = PurchaseStatusForm(current_status=purchase.status)
    
    context = {
        'form': form,
        'purchase': purchase
    }
    
    return render(request, 'dashboard/purchase_status_form.html', context)


@login_required
def my_purchases(request):
    """
    Listar compras do utilizador
    """
    # Compras como comprador
    purchases = Purchase.objects.filter(buyer=request.user).order_by('-created_at')
    
    # Solicitações como comprador
    purchase_requests = PurchaseRequest.objects.filter(buyer=request.user).order_by('-created_at')
    
    # Paginação
    purchase_paginator = Paginator(purchases, 10)
    purchase_page = request.GET.get('purchase_page')
    purchase_obj = purchase_paginator.get_page(purchase_page)
    
    request_paginator = Paginator(purchase_requests, 10)
    request_page = request.GET.get('request_page')
    request_obj = request_paginator.get_page(request_page)
    
    context = {
        'purchases': purchase_obj,
        'purchase_requests': request_obj,
        'active_tab': request.GET.get('tab', 'purchases')
    }
    
    return render(request, 'dashboard/my_purchases.html', context)


@login_required
def my_sales(request):
    """
    Listar vendas do utilizador (vendedor)
    """
    # Vendas como vendedor
    sales = Purchase.objects.filter(seller=request.user).order_by('-created_at')
    
    # Solicitações recebidas como vendedor
    purchase_requests = PurchaseRequest.objects.filter(seller=request.user).order_by('-created_at')
    
    # Paginação
    sales_paginator = Paginator(sales, 10)
    sales_page = request.GET.get('sales_page')
    sales_obj = sales_paginator.get_page(sales_page)
    
    request_paginator = Paginator(purchase_requests, 10)
    request_page = request.GET.get('request_page')
    request_obj = request_paginator.get_page(request_page)
    
    context = {
        'sales': sales_obj,
        'purchase_requests': request_obj,
        'active_tab': request.GET.get('tab', 'sales')
    }
    
    return render(request, 'dashboard/my_sales.html', context)


@login_required
def notifications_list(request):
    """
    Listar notificações do utilizador
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginação
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': notifications.filter(is_read=False).count()
    }
    
    return render(request, 'dashboard/notifications.html', context)


@login_required
def notification_mark_read(request, notification_id):
    """
    Marcar notificação como lida
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('dashboard:notifications')


@login_required
def notifications_mark_all_read(request):
    """
    Marcar todas as notificações como lidas
    """
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Todas as notificações foram marcadas como lidas.')
    return redirect('dashboard:notifications')
