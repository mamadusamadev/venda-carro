import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from cars.models import ChatRoom, ChatMessage, ChatNotification

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Verificar permissões
        chat_room = await self.get_chat_room()
        if not chat_room or not await self.user_has_permission(chat_room):
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notificar que o utilizador está online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': str(self.user.id),
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Notificar que o utilizador está offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': str(self.user.id),
                    'status': 'offline'
                }
            )
            
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')
            
            if action == 'send_message':
                await self.send_message(text_data_json)
            elif action == 'typing':
                await self.handle_typing(text_data_json)
            elif action == 'mark_read':
                await self.mark_messages_read()
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'JSON inválido'
            }))

    async def send_message(self, data):
        message_content = data.get('message', '').strip()
        message_type = data.get('type', 'text')
        
        if not message_content:
            return
        
        chat_room = await self.get_chat_room()
        if not chat_room or chat_room.status != 'active':
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Chat está fechado'
            }))
            return
        
        # Criar mensagem na base de dados
        message = await self.create_message(chat_room, message_content, message_type)
        
        if message:
            # Criar notificação para o outro utilizador
            await self.create_notification(chat_room, message)
            
            # Enviar mensagem para o grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': str(message.id),
                    'message': message_content,
                    'message_type': message_type,
                    'sender_id': str(self.user.id),
                    'sender_username': self.user.username,
                    'sender_name': self.user.get_full_name() or self.user.username,
                    'timestamp': message.created_at.isoformat(),
                    'is_edited': False
                }
            )

    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'is_typing': is_typing
            }
        )

    async def mark_messages_read(self):
        chat_room = await self.get_chat_room()
        if chat_room:
            await self.mark_room_as_read(chat_room)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': str(self.user.id)
                }
            )

    # Handlers para mensagens do grupo
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'message': event['message'],
            'message_type': event['message_type'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
            'is_edited': event['is_edited']
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'status': event['status']
        }))

    async def typing_indicator(self, event):
        if event['user_id'] != str(self.user.id):  # Não enviar para si próprio
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'is_typing': event['is_typing']
            }))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'user_id': event['user_id']
        }))

    # Database operations
    @database_sync_to_async
    def get_chat_room(self):
        try:
            return ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def user_has_permission(self, chat_room):
        return self.user == chat_room.buyer or self.user == chat_room.seller

    @database_sync_to_async
    def create_message(self, chat_room, content, message_type):
        try:
            return ChatMessage.objects.create(
                chat_room=chat_room,
                sender=self.user,
                content=content,
                message_type=message_type
            )
        except Exception:
            return None

    @database_sync_to_async
    def create_notification(self, chat_room, message):
        try:
            other_user = chat_room.get_other_user(self.user)
            if other_user:
                ChatNotification.objects.create(
                    recipient=other_user,
                    chat_room=chat_room,
                    message=message,
                    notification_type='new_message',
                    title=f'Nova mensagem de {self.user.get_full_name() or self.user.username}',
                    content=message.content[:100] + ('...' if len(message.content) > 100 else '')
                )
        except Exception:
            pass

    @database_sync_to_async
    def mark_room_as_read(self, chat_room):
        try:
            chat_room.mark_as_read(self.user)
        except Exception:
            pass