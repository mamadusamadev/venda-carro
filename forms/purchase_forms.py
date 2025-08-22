from django import forms
from django.forms import TextInput, EmailInput, Textarea, NumberInput, Select
from cars.models_purchase import PurchaseRequest, Purchase


class PurchaseRequestForm(forms.ModelForm):
    """
    Formulário para solicitação de compra
    """
    
    class Meta:
        model = PurchaseRequest
        fields = [
            'buyer_name', 'buyer_email', 'buyer_phone', 'buyer_address',
            'buyer_city', 'buyer_postal_code', 'proposed_price', 'message'
        ]
        
        widgets = {
            'buyer_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo',
                'required': True
            }),
            'buyer_email': EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com',
                'required': True
            }),
            'buyer_phone': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+351 912 345 678',
                'required': True
            }),
            'buyer_address': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Morada completa',
                'rows': 3,
                'required': True
            }),
            'buyer_city': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'required': True
            }),
            'buyer_postal_code': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1000-001',
                'required': True
            }),
            'proposed_price': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Preço proposto (opcional)',
                'step': '0.01',
                'min': '0'
            }),
            'message': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mensagem para o vendedor (motivo da compra, quando quer ver o carro, etc.)',
                'rows': 4,
                'required': True
            })
        }
        
        labels = {
            'buyer_name': 'Nome Completo',
            'buyer_email': 'Email',
            'buyer_phone': 'Telefone',
            'buyer_address': 'Morada',
            'buyer_city': 'Cidade',
            'buyer_postal_code': 'Código Postal',
            'proposed_price': 'Preço Proposto (Opcional)',
            'message': 'Mensagem para o Vendedor'
        }
        
        help_texts = {
            'proposed_price': 'Deixe em branco se aceitar o preço anunciado',
            'message': 'Descreva o seu interesse no carro, quando gostaria de vê-lo, etc.'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pré-preencher campos se o utilizador estiver logado
        if self.user and self.user.is_authenticated:
            self.fields['buyer_name'].initial = self.user.get_full_name() or self.user.username
            self.fields['buyer_email'].initial = self.user.email
            if hasattr(self.user, 'phone') and self.user.phone:
                self.fields['buyer_phone'].initial = self.user.phone


class PurchaseForm(forms.ModelForm):
    """
    Formulário para compra direta
    """
    
    accept_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Aceito os termos e condições'
    )
    
    payment_security_warning = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Compreendo que NÃO devo fazer pagamentos fora da plataforma'
    )
    
    class Meta:
        model = Purchase
        fields = [
            'buyer_name', 'buyer_email', 'buyer_phone', 'buyer_address',
            'buyer_city', 'buyer_postal_code', 'notes'
        ]
        
        widgets = {
            'buyer_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo',
                'required': True
            }),
            'buyer_email': EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com',
                'required': True
            }),
            'buyer_phone': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+351 912 345 678',
                'required': True
            }),
            'buyer_address': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Morada completa para entrega',
                'rows': 3,
                'required': True
            }),
            'buyer_city': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'required': True
            }),
            'buyer_postal_code': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1000-001',
                'required': True
            }),
            'notes': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionais (opcional)',
                'rows': 3
            })
        }
        
        labels = {
            'buyer_name': 'Nome Completo',
            'buyer_email': 'Email',
            'buyer_phone': 'Telefone',
            'buyer_address': 'Morada de Entrega',
            'buyer_city': 'Cidade',
            'buyer_postal_code': 'Código Postal',
            'notes': 'Notas Adicionais'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.car = kwargs.pop('car', None)
        super().__init__(*args, **kwargs)
        
        # Pré-preencher campos se o utilizador estiver logado
        if self.user and self.user.is_authenticated:
            self.fields['buyer_name'].initial = self.user.get_full_name() or self.user.username
            self.fields['buyer_email'].initial = self.user.email
            if hasattr(self.user, 'phone') and self.user.phone:
                self.fields['buyer_phone'].initial = self.user.phone


class SellerResponseForm(forms.ModelForm):
    """
    Formulário para resposta do vendedor a uma solicitação de compra
    """
    
    class Meta:
        model = PurchaseRequest
        fields = ['status', 'seller_response']
        
        widgets = {
            'status': Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'seller_response': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Resposta para o comprador...',
                'rows': 4,
                'required': True
            })
        }
        
        labels = {
            'status': 'Decisão',
            'seller_response': 'Resposta'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limitar opções de status para vendedor
        self.fields['status'].choices = [
            ('accepted', 'Aceitar Solicitação'),
            ('rejected', 'Rejeitar Solicitação'),
            ('negotiating', 'Iniciar Negociação'),
        ]


class PurchaseStatusForm(forms.ModelForm):
    """
    Formulário para atualizar status de compra (vendedor)
    """
    
    notes = forms.CharField(
        widget=Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Notas sobre a mudança de status...',
            'rows': 3
        }),
        label='Notas',
        required=False
    )
    
    class Meta:
        model = Purchase
        fields = ['status']
        
        widgets = {
            'status': Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }
        
        labels = {
            'status': 'Novo Status'
        }
    
    def __init__(self, *args, **kwargs):
        current_status = kwargs.pop('current_status', None)
        super().__init__(*args, **kwargs)
        
        # Definir opções de status baseadas no status atual
        if current_status == 'pending_payment':
            self.fields['status'].choices = [
                ('payment_confirmed', 'Confirmar Pagamento'),
                ('cancelled', 'Cancelar Compra'),
            ]
        elif current_status == 'payment_confirmed':
            self.fields['status'].choices = [
                ('preparing_delivery', 'Preparar Entrega'),
                ('cancelled', 'Cancelar Compra'),
            ]
        elif current_status == 'preparing_delivery':
            self.fields['status'].choices = [
                ('in_transit', 'Enviar/Em Trânsito'),
            ]
        elif current_status == 'in_transit':
            self.fields['status'].choices = [
                ('delivered', 'Marcar como Entregue'),
            ]
        elif current_status == 'delivered':
            self.fields['status'].choices = [
                ('completed', 'Concluir Venda'),
            ]
        else:
            # Status padrão
            self.fields['status'].choices = Purchase.STATUS_CHOICES
