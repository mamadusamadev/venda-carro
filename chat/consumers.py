import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from cars.models_chat import ChatRoom, ChatMessage, ChatNotification
from cars.models import Car

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Verificar se o utilizador tem acesso a esta sala
        if not await self.has_room_access():
            await self.close()
            return

        # Juntar-se ao grupo da sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Marcar mensagens como lidas quando o utilizador se conecta
        await self.mark_messages_as_read()

        # Notificar outros utilizadores que este utilizador está online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Notificar outros utilizadores que este utilizador está offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': str(self.user.id),
                    'username': self.user.username,
                    'status': 'offline'
                }
            )

            # Sair do grupo da sala
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')

            if action == 'send_message':
                await self.handle_send_message(text_data_json)
            elif action == 'mark_as_read':
                await self.handle_mark_as_read()
            elif action == 'typing':
                await self.handle_typing(text_data_json)
            elif action == 'close_chat':
                await self.handle_close_chat()

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Formato de mensagem inválido'
            }))

    async def handle_send_message(self, data):
        message_content = data.get('message', '').strip()
        message_type = data.get('type', 'text')

        if not message_content:
            return

        # Criar mensagem na base de dados
        message = await self.create_message(message_content, message_type)

        if message:
            # Obter informações do outro utilizador para notificação
            other_user = await self.get_other_user()

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
                }
            )

            # Criar notificação para o outro utilizador
            if other_user:
                await self.create_chat_notification(other_user, message)

    async def handle_mark_as_read(self):
        await self.mark_messages_as_read()
        
        # Notificar que as mensagens foram lidas
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'messages_read',
                'user_id': str(self.user.id)
            }
        )

    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        # Enviar indicador de digitação para outros utilizadores
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing
            }
        )

    async def handle_close_chat(self):
        # Fechar o chat
        await self.close_chat_room()
        
        # Notificar que o chat foi fechado
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_closed',
                'closed_by_id': str(self.user.id),
                'closed_by_username': self.user.username
            }
        )

    # Handlers para diferentes tipos de mensagens do grupo
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
        }))

    async def user_status(self, event):
        # Não enviar status para o próprio utilizador
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'user_status',
                'user_id': event['user_id'],
                'username': event['username'],
                'status': event['status']
            }))

    async def typing_indicator(self, event):
        # Não enviar indicador de digitação para o próprio utilizador
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    async def messages_read(self, event):
        # Não enviar confirmação de leitura para o próprio utilizador
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'messages_read',
                'user_id': event['user_id']
            }))

    async def chat_closed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_closed',
            'closed_by_id': event['closed_by_id'],
            'closed_by_username': event['closed_by_username']
        }))

    # Funções auxiliares para base de dados
    @database_sync_to_async
    def has_room_access(self):
        """Verificar se o utilizador tem acesso à sala de chat"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            return self.user == chat_room.buyer or self.user == chat_room.seller
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, content, message_type):
        """Criar nova mensagem na base de dados"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=self.user,
                content=content,
                message_type=message_type
            )
            return message
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_messages_as_read(self):
        """Marcar mensagens como lidas para o utilizador atual"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            chat_room.mark_as_read(self.user)
        except ChatRoom.DoesNotExist:
            pass

    @database_sync_to_async
    def get_other_user(self):
        """Obter o outro utilizador da conversa"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            return chat_room.get_other_user(self.user)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def close_chat_room(self):
        """Fechar a sala de chat"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            chat_room.close_chat(self.user)
        except ChatRoom.DoesNotExist:
            pass

    @database_sync_to_async
    def create_chat_notification(self, recipient, message):
        """Criar notificação de chat para o destinatário"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            ChatNotification.objects.create(
                recipient=recipient,
                chat_room=chat_room,
                message=message,
                notification_type='new_message',
                title=f'Nova mensagem de {self.user.get_full_name() or self.user.username}',
                content=message.content[:100] + ('...' if len(message.content) > 100 else '')
            )
        except ChatRoom.DoesNotExist:
            pass
