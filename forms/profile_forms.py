from django import forms
from django.contrib.auth import get_user_model
from accounts.models import SellerProfile, BuyerProfile

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    """Formulário para editar informações básicas do utilizador"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 
            'birth_date', 'avatar', 'city', 'district'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome próprio'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apelido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+351 123 456 789'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lisboa'
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lisboa'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar email obrigatório
        self.fields['email'].required = True
        
        # Adicionar labels personalizadas
        self.fields['first_name'].label = 'Nome Próprio'
        self.fields['last_name'].label = 'Apelido'
        self.fields['email'].label = 'Email'
        self.fields['phone'].label = 'Telefone'
        self.fields['birth_date'].label = 'Data de Nascimento'
        self.fields['avatar'].label = 'Foto de Perfil'
        self.fields['city'].label = 'Cidade'
        self.fields['district'].label = 'Distrito'


class SellerProfileForm(forms.ModelForm):
    """Formulário para editar perfil de vendedor"""
    
    class Meta:
        model = SellerProfile
        fields = [
            'seller_type', 'company_name', 'nif', 'address', 
            'city', 'district', 'postal_code', 'business_hours',
            'description', 'website', 'facebook_url', 
            'instagram_url', 'linkedin_url'
        ]
        widgets = {
            'seller_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da empresa/stand'
            }),
            'nif': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua/Avenida, número'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lisboa'
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lisboa'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1000-100'
            }),
            'business_hours': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ex: Segunda a Sexta: 9h-18h\nSábado: 9h-13h'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva a sua empresa/atividade'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.exemplo.com'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/...'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/...'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Labels personalizadas
        self.fields['seller_type'].label = 'Tipo de Vendedor'
        self.fields['company_name'].label = 'Nome da Empresa/Stand'
        self.fields['nif'].label = 'NIF'
        self.fields['address'].label = 'Morada Comercial'
        self.fields['city'].label = 'Cidade'
        self.fields['district'].label = 'Distrito'
        self.fields['postal_code'].label = 'Código Postal'
        self.fields['business_hours'].label = 'Horário de Funcionamento'
        self.fields['description'].label = 'Descrição'
        self.fields['website'].label = 'Website'
        self.fields['facebook_url'].label = 'Facebook'
        self.fields['instagram_url'].label = 'Instagram'
        self.fields['linkedin_url'].label = 'LinkedIn'


class BuyerProfileForm(forms.ModelForm):
    """Formulário para editar perfil de comprador"""
    
    class Meta:
        model = BuyerProfile
        fields = [
            'preferred_brands', 'budget_min', 'budget_max',
            'fuel_types', 'year_min', 'year_max', 'max_mileage',
            'notifications_email', 'notifications_sms', 'notifications_push',
            'price_alerts', 'new_car_alerts'
        ]
        widgets = {
            'preferred_brands': forms.CheckboxSelectMultiple(),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5000',
                'min': '0'
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '50000',
                'min': '0'
            }),
            'fuel_types': forms.CheckboxSelectMultiple(),
            'year_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2000',
                'min': '1900'
            }),
            'year_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2024',
                'min': '1900'
            }),
            'max_mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '200000',
                'min': '0'
            }),
            'notifications_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notifications_sms': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notifications_push': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'price_alerts': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'new_car_alerts': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Labels personalizadas
        self.fields['preferred_brands'].label = 'Marcas Preferidas'
        self.fields['budget_min'].label = 'Orçamento Mínimo (€)'
        self.fields['budget_max'].label = 'Orçamento Máximo (€)'
        self.fields['fuel_types'].label = 'Tipos de Combustível'
        self.fields['year_min'].label = 'Ano Mínimo'
        self.fields['year_max'].label = 'Ano Máximo'
        self.fields['max_mileage'].label = 'Quilometragem Máxima'
        self.fields['notifications_email'].label = 'Notificações por Email'
        self.fields['notifications_sms'].label = 'Notificações por SMS'
        self.fields['notifications_push'].label = 'Notificações Push'
        self.fields['price_alerts'].label = 'Alertas de Preço'
        self.fields['new_car_alerts'].label = 'Alertas de Carros Novos'


class PasswordChangeForm(forms.Form):
    """Formulário para alterar palavra-passe"""
    
    current_password = forms.CharField(
        label='Palavra-passe Atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Palavra-passe atual'
        })
    )
    
    new_password = forms.CharField(
        label='Nova Palavra-passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nova palavra-passe'
        }),
        help_text='A palavra-passe deve ter pelo menos 8 caracteres.'
    )
    
    confirm_password = forms.CharField(
        label='Confirmar Palavra-passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova palavra-passe'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Palavra-passe atual incorreta.')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('As palavras-passe não coincidem.')
            
            if len(new_password) < 8:
                raise forms.ValidationError('A palavra-passe deve ter pelo menos 8 caracteres.')

        return cleaned_data
