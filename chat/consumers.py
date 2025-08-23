import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from cars.models import ChatRoom, ChatMessage, ChatNotification

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    # Dicionário para rastrear utilizadores online por sala
    online_users = {}
    
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
        
        # Adicionar utilizador à lista de online para esta sala
        if self.room_group_name not in self.online_users:
            self.online_users[self.room_group_name] = set()
        self.online_users[self.room_group_name].add(str(self.user.id))
        
        print(f"Utilizador {self.user.username} conectado. Online na sala: {self.online_users[self.room_group_name]}")
        
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
            # Remover utilizador da lista de online para esta sala
            if self.room_group_name in self.online_users:
                self.online_users[self.room_group_name].discard(str(self.user.id))
                if not self.online_users[self.room_group_name]:
                    del self.online_users[self.room_group_name]
            
            print(f"Utilizador {self.user.username} desconectado. Online na sala: {self.online_users.get(self.room_group_name, set())}")
            
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
            
            print(f"WebSocket recebeu ação: {action}")
            print(f"Dados recebidos: {text_data_json.keys()}")
            
            if action == 'send_message':
                await self.send_message(text_data_json)
            elif action == 'typing':
                await self.handle_typing(text_data_json)
            elif action == 'mark_read':
                await self.mark_messages_read()
            elif action == 'request_status':
                await self.send_current_status()
                
        except json.JSONDecodeError:
            print(f"Erro JSON: {text_data}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'JSON inválido'
            }))
        except Exception as e:
            print(f"Erro no receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Erro interno: {str(e)}'
            }))

    async def send_message(self, data):
        message_content = data.get('message', '').strip()
        message_type = data.get('type', 'text')
        file_data = data.get('file_data')
        file_name = data.get('file_name')
        
        print(f"send_message chamado:")
        print(f"  - message_content: '{message_content}'")
        print(f"  - file_data presente: {bool(file_data)}")
        print(f"  - file_name: {file_name}")
        
        chat_room = await self.get_chat_room()
        if not chat_room or chat_room.status != 'active':
            print("Chat não está ativo")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Chat está fechado'
            }))
            return
        
        # Validar se há conteúdo (texto ou arquivo)
        if not message_content and not file_data:
            print("Nenhum conteúdo para enviar")
            return
        
        # Criar mensagem na base de dados
        message = await self.create_message(chat_room, message_content, message_type, file_data, file_name)
        
        if message:
            # Criar notificação para o outro utilizador
            await self.create_notification(chat_room, message)
            
            # Preparar dados da mensagem
            message_data = {
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
            
            # Adicionar informações do arquivo se existir
            if message.attachment:
                message_data.update({
                    'attachment_url': message.attachment.url,
                    'attachment_name': message.attachment_name or message.attachment.name,
                    'file_size': await self.get_file_size_formatted(message),
                    'file_icon': await self.get_file_icon(message),
                    'is_image': await self.is_image(message)
                })
            
            # Enviar mensagem para o grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                message_data
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

    async def send_current_status(self):
        """Enviar status atual de todos os utilizadores conectados"""
        print(f"Enviando status atual para {self.user.username}")
        
        # Obter a lista de utilizadores online nesta sala
        online_in_room = self.online_users.get(self.room_group_name, set())
        print(f"Utilizadores online na sala: {online_in_room}")
        
        # Obter informações da sala de chat
        chat_room = await self.get_chat_room()
        if chat_room:
            # Obter o outro utilizador da conversa usando database_sync_to_async
            other_user = await self.get_other_user(chat_room)
            
            if other_user:
                other_user_id = str(other_user.id)
                is_other_online = other_user_id in online_in_room
                status = 'online' if is_other_online else 'offline'
                
                print(f"Outro utilizador {other_user.username} está {status}")
                
                # Enviar status do outro utilizador para este utilizador
                await self.send(text_data=json.dumps({
                    'type': 'user_status',
                    'user_id': other_user_id,
                    'status': status
                }))

    # Handlers para mensagens do grupo
    async def chat_message(self, event):
        message_data = {
            'type': 'message',
            'message_id': event['message_id'],
            'message': event['message'],
            'message_type': event['message_type'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
            'is_edited': event['is_edited']
        }
        
        # Adicionar informações do anexo se existir
        if 'attachment_url' in event:
            message_data.update({
                'attachment_url': event['attachment_url'],
                'attachment_name': event['attachment_name'],
                'file_size': event['file_size'],
                'file_icon': event['file_icon'],
                'is_image': event['is_image']
            })
            
        print(f"Enviando mensagem via WebSocket: {message_data.keys()}")
        await self.send(text_data=json.dumps(message_data))

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
    def get_other_user(self, chat_room):
        """Obter o outro utilizador da conversa (não o atual)"""
        if chat_room.buyer != self.user:
            return chat_room.buyer
        elif chat_room.seller != self.user:
            return chat_room.seller
        return None

    @database_sync_to_async
    def user_has_permission(self, chat_room):
        return self.user == chat_room.buyer or self.user == chat_room.seller

    @database_sync_to_async
    def create_message(self, chat_room, content, message_type, file_data=None, file_name=None):
        try:
            from django.core.files.base import ContentFile
            import base64
            
            message = ChatMessage(
                chat_room=chat_room,
                sender=self.user,
                content=content,
                message_type=message_type
            )
            
            # Se há dados de arquivo, processar
            if file_data and file_name:
                # Decodificar dados base64
                format, imgstr = file_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Criar arquivo a partir dos dados
                file_content = ContentFile(base64.b64decode(imgstr), name=file_name)
                message.attachment = file_content
                message.attachment_name = file_name
                
                # Determinar tipo da mensagem baseado no arquivo
                if ext.lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']:
                    message.message_type = 'image'
                else:
                    message.message_type = 'file'
            
            message.save()
            return message
        except Exception as e:
            print(f"Erro ao criar mensagem: {e}")
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
    
    @database_sync_to_async
    def get_file_size_formatted(self, message):
        return message.get_file_size_formatted()
    
    @database_sync_to_async
    def get_file_icon(self, message):
        return message.get_file_icon()
    
    @database_sync_to_async
    def is_image(self, message):
        return message.is_image()