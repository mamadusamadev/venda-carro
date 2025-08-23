import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from cars.models import Car

User = get_user_model()


class ChatRoom(models.Model):
    """
    Sala de chat entre comprador e vendedor sobre um carro específico
    """
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('closed', 'Fechado'),
        ('archived', 'Arquivado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='chat_rooms', verbose_name='Carro')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_chats', verbose_name='Comprador')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_chats', verbose_name='Vendedor')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Status')
    
    # Controle de atividade
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Última atividade')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fechado em')
    closed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='closed_chats',
        verbose_name='Fechado por'
    )
    
    # Controle de leitura
    buyer_last_read = models.DateTimeField(null=True, blank=True, verbose_name='Última leitura do comprador')
    seller_last_read = models.DateTimeField(null=True, blank=True, verbose_name='Última leitura do vendedor')
    
    class Meta:
        verbose_name = 'Sala de Chat'
        verbose_name_plural = 'Salas de Chat'
        unique_together = ['car', 'buyer']  # Um comprador só pode ter um chat por carro
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['car', 'status']),
            models.Index(fields=['-last_activity']),
        ]

    def __str__(self):
        return f"Chat: {self.buyer.username} <-> {self.seller.username} sobre {self.car.title}"

    @property
    def room_name(self):
        """Nome único da sala para WebSocket"""
        return f"chat_{self.id}"

    def get_unread_count_for_user(self, user):
        """Obter número de mensagens não lidas para um utilizador"""
        if user == self.buyer:
            last_read = self.buyer_last_read
        elif user == self.seller:
            last_read = self.seller_last_read
        else:
            return 0
        
        if last_read:
            return self.messages.filter(created_at__gt=last_read).exclude(sender=user).count()
        else:
            return self.messages.exclude(sender=user).count()

    def mark_as_read(self, user):
        """Marcar como lido para um utilizador"""
        now = timezone.now()
        if user == self.buyer:
            self.buyer_last_read = now
        elif user == self.seller:
            self.seller_last_read = now
        self.save(update_fields=['buyer_last_read', 'seller_last_read'])

    def close_chat(self, user):
        """Fechar o chat"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.closed_by = user
        self.save(update_fields=['status', 'closed_at', 'closed_by'])

    def reopen_chat(self):
        """Reabrir o chat"""
        self.status = 'active'
        self.closed_at = None
        self.closed_by = None
        self.save(update_fields=['status', 'closed_at', 'closed_by'])

    def get_other_user(self, current_user):
        """Obter o outro utilizador do chat"""
        if current_user == self.buyer:
            return self.seller
        elif current_user == self.seller:
            return self.buyer
        return None


class ChatMessage(models.Model):
    """
    Mensagem individual dentro de uma sala de chat
    """
    MESSAGE_TYPES = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('file', 'Ficheiro'),
        ('system', 'Sistema'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name='Sala de Chat')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages_sent', verbose_name='Remetente')
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text', verbose_name='Tipo de Mensagem')
    content = models.TextField(verbose_name='Conteúdo')
    
    # Anexos (opcional)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True, verbose_name='Anexo')
    attachment_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nome do Anexo')
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Enviado em')
    edited_at = models.DateTimeField(null=True, blank=True, verbose_name='Editado em')
    is_edited = models.BooleanField(default=False, verbose_name='Foi editado')
    is_deleted = models.BooleanField(default=False, verbose_name='Foi apagado')
    
    class Meta:
        verbose_name = 'Mensagem de Chat'
        verbose_name_plural = 'Mensagens de Chat'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat_room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualizar última atividade da sala
        self.chat_room.last_activity = self.created_at
        self.chat_room.save(update_fields=['last_activity'])

    def delete_message(self):
        """Marcar mensagem como apagada (soft delete)"""
        self.is_deleted = True
        self.content = "[Mensagem apagada]"
        self.save(update_fields=['is_deleted', 'content'])

    def edit_message(self, new_content):
        """Editar mensagem"""
        self.content = new_content
        self.edited_at = timezone.now()
        self.is_edited = True
        self.save(update_fields=['content', 'edited_at', 'is_edited'])


class ChatNotification(models.Model):
    """
    Notificações específicas do sistema de chat
    """
    NOTIFICATION_TYPES = [
        ('new_message', 'Nova Mensagem'),
        ('chat_started', 'Chat Iniciado'),
        ('chat_closed', 'Chat Fechado'),
        ('chat_reopened', 'Chat Reaberto'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_notifications', verbose_name='Destinatário')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='notifications', verbose_name='Sala de Chat')
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Mensagem')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='Tipo de Notificação')
    title = models.CharField(max_length=200, verbose_name='Título')
    content = models.TextField(verbose_name='Conteúdo')
    
    is_read = models.BooleanField(default=False, verbose_name='Foi lida')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criada em')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Lida em')
    
    class Meta:
        verbose_name = 'Notificação de Chat'
        verbose_name_plural = 'Notificações de Chat'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Notificação para {self.recipient.username}: {self.title}"

    def mark_as_read(self):
        """Marcar notificação como lida"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
