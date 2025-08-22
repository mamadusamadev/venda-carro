from django import forms
from django.forms import TextInput, EmailInput, PasswordInput, Select, CheckboxInput
from accounts.models import User


class RegisterForm(forms.ModelForm):
    password_confirmation = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a palavra-passe'
        })
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'user_type']
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de utilizador'
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'password': PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Palavra-passe'
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primeiro nome'
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Último nome'
            }),
            'phone': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefone'
            }),
            'user_type': Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        
        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("As palavras-passe não coincidem.")
        
        return password_confirmation

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está registado.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de utilizador já existe.")
        return username


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    password = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Palavra-passe'
        })
    )


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone']
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control'
            }),
            'email': EmailInput(attrs={
                'class': 'form-control'
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control'
            }),
            'phone': TextInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este nome de utilizador já existe.")
        return username


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Palavra-passe atual'
        })
    )
    
    new_password = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nova palavra-passe'
        })
    )
    
    new_password_confirmation = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova palavra-passe'
        })
    )

    def clean_new_password_confirmation(self):
        new_password = self.cleaned_data.get('new_password')
        new_password_confirmation = self.cleaned_data.get('new_password_confirmation')
        
        if new_password and new_password_confirmation and new_password != new_password_confirmation:
            raise forms.ValidationError("As palavras-passe não coincidem.")
        
        return new_password_confirmation 