from django.db import models
from django.contrib.auth import get_user_model
from cars.models import Car
import uuid

User = get_user_model()


class PurchaseRequest(models.Model):
    """
    Modelo para solicitações de compra (primeira modalidade)
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceite pelo Vendedor'),
        ('rejected', 'Rejeitada'),
        ('negotiating', 'Em Negociação'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='purchase_requests')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_purchase_requests')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_purchase_requests')
    
    # Informações do comprador
    buyer_name = models.CharField(max_length=200, verbose_name='Nome Completo')
    buyer_email = models.EmailField(verbose_name='Email')
    buyer_phone = models.CharField(max_length=20, verbose_name='Telefone')
    buyer_address = models.TextField(verbose_name='Morada')
    buyer_city = models.CharField(max_length=100, verbose_name='Cidade')
    buyer_postal_code = models.CharField(max_length=20, verbose_name='Código Postal')
    
    # Proposta
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Preço Proposto')
    message = models.TextField(verbose_name='Mensagem', help_text='Mensagem para o vendedor')
    
    # Status e datas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Resposta do vendedor
    seller_response = models.TextField(blank=True, verbose_name='Resposta do Vendedor')
    seller_responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Solicitação de Compra'
        verbose_name_plural = 'Solicitações de Compra'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Solicitação de {self.buyer_name} para {self.car.title}"


class Purchase(models.Model):
    """
    Modelo para compras diretas (segunda modalidade)
    """
    STATUS_CHOICES = [
        ('pending_payment', 'Aguardando Pagamento'),
        ('payment_confirmed', 'Pagamento Confirmado'),
        ('preparing_delivery', 'Preparando Entrega'),
        ('in_transit', 'Em Trânsito'),
        ('delivered', 'Entregue'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
        ('refunded', 'Reembolsada'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhado'),
        ('refunded', 'Reembolsado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='purchases')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    
    # Informações do comprador
    buyer_name = models.CharField(max_length=200, verbose_name='Nome Completo')
    buyer_email = models.EmailField(verbose_name='Email')
    buyer_phone = models.CharField(max_length=20, verbose_name='Telefone')
    buyer_address = models.TextField(verbose_name='Morada de Entrega')
    buyer_city = models.CharField(max_length=100, verbose_name='Cidade')
    buyer_postal_code = models.CharField(max_length=20, verbose_name='Código Postal')
    
    # Informações da compra
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço da Compra')
    notes = models.TextField(blank=True, verbose_name='Notas Adicionais')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Datas importantes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Informações de pagamento (para quando implementarmos gateway)
    payment_method = models.CharField(max_length=50, blank=True, verbose_name='Método de Pagamento')
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name='ID da Transação')
    
    # Tracking
    tracking_code = models.CharField(max_length=100, blank=True, verbose_name='Código de Rastreamento')
    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['payment_status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Compra de {self.buyer_name} - {self.car.title}"
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def can_be_cancelled(self):
        return self.status in ['pending_payment', 'payment_confirmed']


class PurchaseStatusHistory(models.Model):
    """
    Histórico de mudanças de status das compras
    """
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Histórico de Status'
        verbose_name_plural = 'Histórico de Status'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.previous_status} → {self.new_status} ({self.created_at})"


class Notification(models.Model):
    """
    Sistema de notificações
    """
    TYPE_CHOICES = [
        ('purchase_request', 'Solicitação de Compra'),
        ('purchase_created', 'Nova Compra'),
        ('status_changed', 'Status Alterado'),
        ('payment_confirmed', 'Pagamento Confirmado'),
        ('delivery_confirmed', 'Entrega Confirmada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Referências opcionais
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, null=True, blank=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, null=True, blank=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = models.timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
