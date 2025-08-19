from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class LoginForm(forms.Form):
    """Formulário de login com email"""
    
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o seu email',
            'required': True,
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label="Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a sua palavra-passe',
            'required': True
        })
    )
    
    remember_me = forms.BooleanField(
        label="Lembrar-me",
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_email(self):
        """Valida o email"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email


class RegisterForm(forms.Form):
    """Formulário de registo"""
    
    USER_TYPE_CHOICES = [
        ('buyer', 'Comprador'),
        ('seller', 'Vendedor'),
        ('both', 'Comprador e Vendedor')
    ]
    
    # Dados pessoais
    first_name = forms.CharField(
        label="Primeiro Nome",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o seu primeiro nome',
            'required': True
        })
    )
    
    last_name = forms.CharField(
        label="Último Nome",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o seu último nome',
            'required': True
        })
    )
    
    # Dados de conta
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o seu email',
            'required': True
        })
    )
    
    username = forms.CharField(
        label="Nome de Utilizador",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome de utilizador',
            'required': True
        })
    )
    
    phone = forms.CharField(
        label="Telefone",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o seu telefone',
            'required': True
        })
    )
    
    # Tipo de utilizador
    user_type = forms.ChoiceField(
        label="Tipo de Conta",
        choices=USER_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    # Palavras-passe
    password = forms.CharField(
        label="Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a sua palavra-passe',
            'required': True
        })
    )
    
    password_confirm = forms.CharField(
        label="Confirmar Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a sua palavra-passe',
            'required': True
        })
    )
    
    # Termos e condições
    terms_accepted = forms.BooleanField(
        label="Aceito os termos e condições",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_email(self):
        """Valida o email"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise ValidationError("Já existe uma conta com este email.")
        return email
    
    def clean_username(self):
        """Valida o username"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower().strip()
            if User.objects.filter(username=username).exists():
                raise ValidationError("Já existe uma conta com este nome de utilizador.")
        return username
    
    def clean_password(self):
        """Valida a palavra-passe"""
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password
    
    def clean(self):
        """Validações gerais do formulário"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError("As palavras-passe não coincidem.")
        
        return cleaned_data


class PasswordChangeForm(forms.Form):
    """Formulário para alterar palavra-passe"""
    
    current_password = forms.CharField(
        label="Palavra-passe Atual",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a sua palavra-passe atual',
            'required': True
        })
    )
    
    new_password = forms.CharField(
        label="Nova Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova palavra-passe',
            'required': True
        })
    )
    
    new_password_confirm = forms.CharField(
        label="Confirmar Nova Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova palavra-passe',
            'required': True
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        """Valida a palavra-passe atual"""
        current_password = self.cleaned_data.get('current_password')
        if current_password and not self.user.check_password(current_password):
            raise ValidationError("Palavra-passe atual incorreta.")
        return current_password
    
    def clean_new_password(self):
        """Valida a nova palavra-passe"""
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            try:
                validate_password(new_password, self.user)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return new_password
    
    def clean(self):
        """Validações gerais do formulário"""
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        
        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise ValidationError("As novas palavras-passe não coincidem.")
        
        return cleaned_data 