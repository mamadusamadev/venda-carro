from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from datetime import datetime, timedelta

User = get_user_model()

class Transaction(models.Model):
    """
    Modelo para transações de compra/venda
    """
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmada'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
        ('refunded', 'Reembolsada'),
        ('disputed', 'Em Disputa'),
    )
    
    TRANSACTION_TYPES = (
        ('sale', 'Venda'),
        ('reservation', 'Reserva'),
        ('deposit', 'Sinal'),
        ('full_payment', 'Pagamento Total'),
        ('commission', 'Comissão'),
        ('refund', 'Reembolso'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Partes envolvidas
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sales'
    )
    
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    # Detalhes da transação
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        verbose_name='Tipo de Transação'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Valores financeiros
    car_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço do Carro (€)'
    )
    
    platform_commission = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Comissão da Plataforma (€)'
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor Total (€)'
    )
    
    # Referências externas
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referência de Pagamento'
    )
    
    invoice_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Número da Fatura'
    )
    
    # Observações e notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    # Datas importantes
    scheduled_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data Agendada'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Conclusão'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['car']),
        ]

    def __str__(self):
        return f"Transação {self.id} - {self.car} - €{self.total_amount}"
    
    def calculate_seller_amount(self):
        """Calcula o valor que o vendedor recebe"""
        return self.car_price - self.platform_commission
    
    def is_completed(self):
        return self.status == 'completed'


class Payment(models.Model):
    """
    Modelo para pagamentos
    """
    PAYMENT_METHODS = (
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('bank_transfer', 'Transferência Bancária'),
        ('mbway', 'MB WAY'),
        ('multibanco', 'Multibanco'),
        ('paypal', 'PayPal'),
        ('cash', 'Dinheiro'),
        ('check', 'Cheque'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('processing', 'A Processar'),
        ('completed', 'Concluído'),
        ('failed', 'Falhado'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    payer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments_made'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor (€)'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name='Método de Pagamento'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Referências externas do processador de pagamentos
    external_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referência Externa'
    )
    
    gateway_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Resposta do Gateway'
    )
    
    # Detalhes do pagamento
    description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    failure_reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Motivo da Falha'
    )
    
    # Datas
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Processamento'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payer', '-created_at']),
            models.Index(fields=['transaction']),
        ]

    def __str__(self):
        return f"Pagamento {self.id} - €{self.amount} ({self.get_status_display()})"


class Reservation(models.Model):
    """
    Modelo para reservas de carros
    """
    STATUS_CHOICES = (
        ('active', 'Ativa'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('expired', 'Expirada'),
        ('completed', 'Concluída'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Estado'
    )
    
    # Valores da reserva
    reservation_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Valor da Reserva (€)'
    )
    
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço Total Acordado (€)'
    )
    
    # Datas importantes
    expires_at = models.DateTimeField(
        verbose_name='Data de Expiração'
    )
    
    meeting_scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Reunião Agendada Para'
    )
    
    # Localização da reunião
    meeting_location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Local da Reunião'
    )
    
    # Observações
    buyer_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas do Comprador'
    )
    
    seller_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas do Vendedor'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['car']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Reserva {self.id} - {self.car} por {self.buyer.username}"
    
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at < timezone.now()
    
    def is_active(self):
        return self.status == 'active' and not self.is_expired()


class TestDrive(models.Model):
    """
    Modelo para agendamento de test drives
    """
    STATUS_CHOICES = (
        ('requested', 'Solicitado'),
        ('confirmed', 'Confirmado'),
        ('completed', 'Realizado'),
        ('cancelled', 'Cancelado'),
        ('no_show', 'Não Compareceu'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='test_drives'
    )
    
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.CASCADE,
        related_name='test_drives'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested',
        verbose_name='Estado'
    )
    
    # Agendamento
    scheduled_date = models.DateTimeField(
        verbose_name='Data e Hora Agendada'
    )
    
    duration_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name='Duração (minutos)'
    )
    
    # Localização
    meeting_address = models.CharField(
        max_length=200,
        verbose_name='Morada de Encontro'
    )
    
    # Requisitos
    driving_license_required = models.BooleanField(
        default=True,
        verbose_name='Carta de Condução Obrigatória'
    )
    
    insurance_required = models.BooleanField(
        default=True,
        verbose_name='Seguro Obrigatório'
    )
    
    # Notas
    buyer_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem do Comprador'
    )
    
    seller_response = models.TextField(
        blank=True,
        null=True,
        verbose_name='Resposta do Vendedor'
    )
    
    # Avaliação pós test drive
    buyer_rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Avaliação do Comprador'
    )
    
    buyer_feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name='Feedback do Comprador'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Test Drive'
        verbose_name_plural = 'Test Drives'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['car']),
            models.Index(fields=['scheduled_date']),
        ]

    def __str__(self):
        return f"Test Drive {self.id} - {self.car} por {self.buyer.username}"


class Invoice(models.Model):
    """
    Modelo para faturas
    """
    STATUS_CHOICES = (
        ('draft', 'Rascunho'),
        ('sent', 'Enviada'),
        ('paid', 'Paga'),
        ('overdue', 'Em Atraso'),
        ('cancelled', 'Cancelada'),
    )
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número da Fatura'
    )
    
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='invoice'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Dados do comprador
    buyer_name = models.CharField(max_length=200, verbose_name='Nome do Comprador')
    buyer_email = models.EmailField(verbose_name='Email do Comprador')
    buyer_address = models.TextField(verbose_name='Morada do Comprador')
    buyer_nif = models.CharField(max_length=15, blank=True, null=True, verbose_name='NIF do Comprador')
    
    # Dados do vendedor
    seller_name = models.CharField(max_length=200, verbose_name='Nome do Vendedor')
    seller_email = models.EmailField(verbose_name='Email do Vendedor')
    seller_address = models.TextField(verbose_name='Morada do Vendedor')
    seller_nif = models.CharField(max_length=15, blank=True, null=True, verbose_name='NIF do Vendedor')
    
    # Valores
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Subtotal (€)')
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), verbose_name='IVA (€)')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total (€)')
    
    # Datas
    issue_date = models.DateField(verbose_name='Data de Emissão')
    due_date = models.DateField(verbose_name='Data de Vencimento')
    paid_date = models.DateField(blank=True, null=True, verbose_name='Data de Pagamento')
    
    # Observações
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['issue_date']),
        ]

    def __str__(self):
        return f"Fatura {self.invoice_number} - €{self.total_amount}"
    
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status != 'paid'


class Dispute(models.Model):
    """
    Modelo para disputas/reclamações
    """
    STATUS_CHOICES = (
        ('open', 'Aberta'),
        ('investigating', 'Em Investigação'),
        ('resolved', 'Resolvida'),
        ('closed', 'Fechada'),
    )
    
    DISPUTE_TYPES = (
        ('payment', 'Problema de Pagamento'),
        ('product', 'Problema com o Carro'),
        ('delivery', 'Problema de Entrega'),
        ('communication', 'Problema de Comunicação'),
        ('fraud', 'Suspeita de Fraude'),
        ('other', 'Outro'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='disputes'
    )
    
    complainant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='filed_disputes'
    )
    
    respondent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='disputes_against'
    )
    
    dispute_type = models.CharField(
        max_length=20,
        choices=DISPUTE_TYPES,
        verbose_name='Tipo de Disputa'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name='Estado'
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name='Assunto'
    )
    
    description = models.TextField(
        verbose_name='Descrição do Problema'
    )
    
    evidence = models.FileField(
        upload_to='disputes/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Evidência'
    )
    
    # Resposta do respondente
    response = models.TextField(
        blank=True,
        null=True,
        verbose_name='Resposta'
    )
    
    response_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data da Resposta'
    )
    
    # Resolução
    resolution = models.TextField(
        blank=True,
        null=True,
        verbose_name='Resolução'
    )
    
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='resolved_disputes'
    )
    
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Resolução'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Disputa'
        verbose_name_plural = 'Disputas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['complainant', '-created_at']),
            models.Index(fields=['dispute_type']),
        ]

    def __str__(self):
        return f"Disputa {self.id} - {self.subject}" 