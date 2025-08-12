# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from authenticate.models  import User, SellerProfile, BuyerProfile

class BuyerRegistrationForm(UserCreationForm):
    """
    Formulário de registro para compradores
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=False)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    # Campos específicos do comprador
    preferred_brands = forms.CharField(
        max_length=500, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Toyota, Honda, Volkswagen'})
    )
    max_budget = forms.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Orçamento máximo'})
    )
    email_notifications = forms.BooleanField(initial=True, required=False)
    sms_notifications = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'birth_date', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.birth_date = self.cleaned_data['birth_date']
        user.user_type = 'buyer'
        
        if commit:
            user.save()
            
            # Criar perfil do comprador
            BuyerProfile.objects.create(
                user=user,
                preferred_brands=self.cleaned_data.get('preferred_brands', ''),
                max_budget=self.cleaned_data.get('max_budget'),
                email_notifications=self.cleaned_data.get('email_notifications', True),
                sms_notifications=self.cleaned_data.get('sms_notifications', False)
            )
        
        return user


class SellerRegistrationForm(UserCreationForm):
    """
    Formulário de registro para vendedores
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)
    
    # Campos específicos do vendedor
    seller_type = forms.ChoiceField(
        choices=SellerProfile.SELLER_TYPES,
        required=True,
        widget=forms.RadioSelect
    )
    
    # Para pessoa jurídica
    company_name = forms.CharField(max_length=200, required=False)
    company_nif = forms.CharField(max_length=15, required=False, label='NIF da Empresa')
    
    # Para pessoa física
    nif = forms.CharField(max_length=10, required=False, label='NIF/Contribuinte')
    
    # Morada (obrigatório para vendedores)
    address = forms.CharField(max_length=200, required=True, label='Morada')
    city = forms.CharField(max_length=100, required=True, label='Cidade')
    district = forms.CharField(max_length=50, required=True, label='Distrito')
    postal_code = forms.CharField(
        max_length=8, 
        required=True, 
        label='Código Postal',
        widget=forms.TextInput(attrs={'placeholder': '0000-000'})
    )
    
    # Informações comerciais
    business_hours = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        required=False
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}), 
        required=False
    )
    website = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        seller_type = cleaned_data.get('seller_type')
        
        # Validações específicas por tipo de vendedor
        if seller_type == 'individual':
            if not cleaned_data.get('nif'):
                raise forms.ValidationError('NIF é obrigatório para pessoa física.')
        elif seller_type in ['dealer', 'company']:
            if not cleaned_data.get('company_name'):
                raise forms.ValidationError('Nome da empresa é obrigatório.')
            if not cleaned_data.get('company_nif'):
                raise forms.ValidationError('NIF da empresa é obrigatório para pessoa jurídica.')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.user_type = 'seller'
        
        if commit:
            user.save()
            
            # Criar perfil do vendedor
            SellerProfile.objects.create(
                user=user,
                seller_type=self.cleaned_data['seller_type'],
                company_name=self.cleaned_data.get('company_name', ''),
                company_nif=self.cleaned_data.get('company_nif', ''),
                nif=self.cleaned_data.get('nif', ''),
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                district=self.cleaned_data['district'],
                postal_code=self.cleaned_data['postal_code'],
                business_hours=self.cleaned_data.get('business_hours', ''),
                description=self.cleaned_data.get('description', ''),
                website=self.cleaned_data.get('website', '')
            )
        
        return user

