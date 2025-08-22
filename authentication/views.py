from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from forms.auth_forms import RegisterForm, LoginForm
from entities.user_entity import User as UserEntity
from service import auth_service


def register_view(request):
    """Registar novo utilizador"""
    if request.method == "POST":
        form_register = RegisterForm(request.POST)
        
        if form_register.is_valid():
            username = form_register.cleaned_data["username"]
            email = form_register.cleaned_data["email"]
            password = form_register.cleaned_data["password"]
            first_name = form_register.cleaned_data["first_name"]
            last_name = form_register.cleaned_data["last_name"]
            phone = form_register.cleaned_data.get("phone", "")
            user_type = form_register.cleaned_data["user_type"]
            
            # Criar entidade User
            user_entity = UserEntity(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                user_type=user_type,
                is_active=True
            )
            
            # Cadastrar utilizador
            user = auth_service.cadastrar_user(user_entity)
            
            if user:
                messages.success(request, f'Conta criada com sucesso! Bem-vindo, {first_name or username}!')
                
                # Fazer login automaticamente
                auth_service.fazer_login(request, user)
                
                # Redirecionar baseado no tipo de utilizador
                if user_type == 'seller':
                    return redirect('dashboard:home')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Erro ao criar conta. Email ou nome de utilizador já existem.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form_register = RegisterForm()
    
    context = {
        'form': form_register
    }
    
    return render(request, 'authentication/register.html', context)


def login_view(request):
    """Login do utilizador"""
    if request.method == "POST":
        form_login = LoginForm(request.POST)
        
        if form_login.is_valid():
            email = form_login.cleaned_data['email']
            password = form_login.cleaned_data['password']
            
            # Autenticar utilizador
            user = auth_service.autenticar_user(email, password)
            
            if user is not None:
                if user.is_active:
                    # Fazer login
                    if auth_service.fazer_login(request, user):
                        messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
                        
                        # Redirecionar para onde o utilizador queria ir ou dashboard
                        next_url = request.GET.get('next', 'dashboard:home')
                        return redirect(next_url)
                    else:
                        messages.error(request, 'Erro ao fazer login. Tente novamente.')
                else:
                    messages.error(request, 'Conta desativada. Contacte o administrador.')
            else:
                messages.error(request, 'Email ou palavra-passe incorretos')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form_login = LoginForm()
    
    context = {
        'form': form_login
    }
    
    return render(request, 'authentication/login.html', context)


def logout_view(request):
    """Logout do utilizador"""
    auth_service.fazer_logout(request)
    messages.success(request, 'Sessão terminada com sucesso!')
    return redirect('home')


def check_username(request):
    """Verificar se username existe (AJAX)"""
    username = request.GET.get('username', '')
    
    if username:
        exists = auth_service.verificar_username_existe(username)
        return JsonResponse({
            'exists': exists,
            'message': 'Nome de utilizador já existe' if exists else 'Nome de utilizador disponível'
        })
    
    return JsonResponse({'exists': False, 'message': ''})


def check_email(request):
    """Verificar se email existe (AJAX)"""
    email = request.GET.get('email', '')
    
    if email:
        exists = auth_service.verificar_email_existe(email)
        return JsonResponse({
            'exists': exists,
            'message': 'Email já registado' if exists else 'Email disponível'
        })
    
    return JsonResponse({'exists': False, 'message': ''})
