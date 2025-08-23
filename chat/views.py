from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count, Max, Case, When

from cars.models import Car
from cars.models_chat import ChatRoom, ChatMessage, ChatNotification


@login_required
def start_chat(request, car_id):
    """
    Iniciar ou continuar um chat sobre um carro específico
    """
    car = get_object_or_404(Car, id=car_id)
    
    # Verificar se o utilizador não é o vendedor
    if car.seller == request.user:
        messages.error(request, 'Não pode iniciar um chat com você mesmo.')
        return redirect('dashboard:car_detail', car_id=car_id)
    
    # Verificar se já existe uma sala de chat
    chat_room, created = ChatRoom.objects.get_or_create(
        car=car,
        buyer=request.user,
        defaults={
            'seller': car.seller,
            'status': 'active'
        }
    )
    
    # Se o chat estava fechado, reabrir
    if chat_room.status == 'closed':
        chat_room.reopen_chat()
        messages.success(request, 'Chat reaberto com sucesso!')
    elif created:
        # Criar notificação para o vendedor sobre novo chat
        ChatNotification.objects.create(
            recipient=car.seller,
            chat_room=chat_room,
            notification_type='chat_started',
            title=f'Novo chat sobre {car.title}',
            content=f'{request.user.get_full_name() or request.user.username} iniciou uma conversa sobre o seu carro.'
        )
        messages.success(request, 'Chat iniciado com sucesso!')
    
    return redirect('chat:chat_room', room_id=chat_room.id)


@login_required
def chat_room(request, room_id):
    """
    Página da sala de chat
    """
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Verificar se o utilizador tem acesso
    if request.user != chat_room.buyer and request.user != chat_room.seller:
        messages.error(request, 'Não tem permissão para aceder a este chat.')
        return redirect('dashboard:home')
    
    # Obter mensagens da conversa
    messages_list = chat_room.messages.filter(is_deleted=False).select_related('sender')
    
    # Marcar mensagens como lidas
    chat_room.mark_as_read(request.user)
    
    # Obter informações do outro utilizador
    other_user = chat_room.get_other_user(request.user)
    
    # Determinar se o utilizador atual é o comprador
    is_buyer = request.user == chat_room.buyer
    
    context = {
        'chat_room': chat_room,
        'messages': messages_list,
        'other_user': other_user,
        'is_buyer': is_buyer,
        'car': chat_room.car,
    }
    
    return render(request, 'chat/chat_room.html', context)


@login_required
def my_chats(request):
    """
    Listar todos os chats do utilizador
    """
    # Obter chats onde o utilizador é comprador ou vendedor
    chats = ChatRoom.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('car', 'buyer', 'seller').annotate(
        unread_count=Count('messages', filter=Q(
            messages__created_at__gt=Case(
                When(buyer=request.user, then='buyer_last_read'),
                When(seller=request.user, then='seller_last_read'),
                default=None
            )
        ) & ~Q(messages__sender=request.user)),
        last_message_time=Max('messages__created_at')
    ).order_by('-last_activity')
    
    # Paginação
    paginator = Paginator(chats, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'chats': page_obj,
        'page_obj': page_obj,
        'total_chats': chats.count()
    }
    
    return render(request, 'chat/my_chats.html', context)


@login_required
def close_chat(request, room_id):
    """
    Fechar um chat
    """
    if request.method == 'POST':
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # Verificar se o utilizador tem acesso
        if request.user != chat_room.buyer and request.user != chat_room.seller:
            return JsonResponse({'success': False, 'error': 'Sem permissão'})
        
        # Fechar o chat
        chat_room.close_chat(request.user)
        
        # Criar notificação para o outro utilizador
        other_user = chat_room.get_other_user(request.user)
        if other_user:
            ChatNotification.objects.create(
                recipient=other_user,
                chat_room=chat_room,
                notification_type='chat_closed',
                title=f'Chat sobre {chat_room.car.title} foi fechado',
                content=f'{request.user.get_full_name() or request.user.username} fechou o chat.'
            )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            messages.success(request, 'Chat fechado com sucesso.')
            return redirect('chat:my_chats')
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@login_required
def chat_notifications(request):
    """
    Listar notificações de chat do utilizador
    """
    notifications = ChatNotification.objects.filter(
        recipient=request.user
    ).select_related('chat_room', 'message').order_by('-created_at')
    
    # Paginação
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'page_obj': page_obj,
        'unread_count': notifications.filter(is_read=False).count()
    }
    
    return render(request, 'chat/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """
    Marcar notificação de chat como lida
    """
    if request.method == 'POST':
        notification = get_object_or_404(ChatNotification, id=notification_id, recipient=request.user)
        notification.mark_as_read()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('chat:chat_room', room_id=notification.chat_room.id)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@login_required
def get_chat_status(request):
    """
    Obter status dos chats (para notificações em tempo real)
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Contar mensagens não lidas
        unread_count = 0
        
        # Chats onde é comprador
        buyer_chats = ChatRoom.objects.filter(buyer=request.user)
        for chat in buyer_chats:
            if chat.buyer_last_read:
                unread_count += chat.messages.filter(
                    created_at__gt=chat.buyer_last_read
                ).exclude(sender=request.user).count()
            else:
                unread_count += chat.messages.exclude(sender=request.user).count()
        
        # Chats onde é vendedor
        seller_chats = ChatRoom.objects.filter(seller=request.user)
        for chat in seller_chats:
            if chat.seller_last_read:
                unread_count += chat.messages.filter(
                    created_at__gt=chat.seller_last_read
                ).exclude(sender=request.user).count()
            else:
                unread_count += chat.messages.exclude(sender=request.user).count()
        
        return JsonResponse({
            'success': True,
            'unread_messages': unread_count
        })
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})


@login_required
def send_message_api(request, room_id):
    """
    API para enviar mensagem via AJAX
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        import json
        
        try:
            data = json.loads(request.body)
            message_content = data.get('message', '').strip()
            message_type = data.get('type', 'text')
            
            if not message_content:
                return JsonResponse({'success': False, 'error': 'Mensagem vazia'})
            
            chat_room = get_object_or_404(ChatRoom, id=room_id)
            
            # Verificar permissões
            if request.user != chat_room.buyer and request.user != chat_room.seller:
                return JsonResponse({'success': False, 'error': 'Sem permissão'})
            
            # Verificar se o chat está ativo
            if chat_room.status != 'active':
                return JsonResponse({'success': False, 'error': 'Chat está fechado'})
            
            # Criar mensagem
            message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=message_content,
                message_type=message_type
            )
            
            # Criar notificação para o outro utilizador
            other_user = chat_room.get_other_user(request.user)
            if other_user:
                ChatNotification.objects.create(
                    recipient=other_user,
                    chat_room=chat_room,
                    message=message,
                    notification_type='new_message',
                    title=f'Nova mensagem de {request.user.get_full_name() or request.user.username}',
                    content=message_content[:100] + ('...' if len(message_content) > 100 else '')
                )
            
            return JsonResponse({
                'success': True,
                'message_id': str(message.id),
                'timestamp': message.created_at.isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@login_required
def get_messages_api(request, room_id):
    """
    API para obter mensagens via AJAX
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # Verificar permissões
        if request.user != chat_room.buyer and request.user != chat_room.seller:
            return JsonResponse({'success': False, 'error': 'Sem permissão'})
        
        last_id = request.GET.get('last_id', '')
        
        # Obter mensagens mais recentes
        messages_query = chat_room.messages.filter(is_deleted=False).select_related('sender')
        
        if last_id:
            try:
                messages_query = messages_query.filter(created_at__gt=ChatMessage.objects.get(id=last_id).created_at)
            except ChatMessage.DoesNotExist:
                pass
        
        messages = messages_query.order_by('created_at')[:10]  # Limitar a 10 mensagens
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': str(message.id),
                'message': message.content,
                'message_type': message.message_type,
                'sender_id': str(message.sender.id),
                'sender_username': message.sender.username,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'timestamp': message.created_at.isoformat(),
                'is_edited': message.is_edited
            })
        
        # Marcar mensagens como lidas
        if messages:
            chat_room.mark_as_read(request.user)
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})