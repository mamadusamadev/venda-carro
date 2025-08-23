from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Iniciar chat
    path('iniciar/<uuid:car_id>/', views.start_chat, name='start_chat'),
    
    # Sala de chat
    path('sala/<uuid:room_id>/', views.chat_room, name='chat_room'),
    
    # Meus chats
    path('meus-chats/', views.my_chats, name='my_chats'),
    
    # Fechar chat
    path('fechar/<uuid:room_id>/', views.close_chat, name='close_chat'),
    
    # Notificações de chat
    path('notificacoes/', views.chat_notifications, name='notifications'),
    path('notificacoes/<uuid:notification_id>/ler/', views.mark_notification_read, name='mark_notification_read'),
    
    # APIs para chat
    path('api/status/', views.get_chat_status, name='get_status'),
    path('api/send/<uuid:room_id>/', views.send_message_api, name='send_message_api'),
    path('api/messages/<uuid:room_id>/', views.get_messages_api, name='get_messages_api'),
    path('api/recent-messages/', views.recent_messages_api, name='recent_messages_api'),
]
