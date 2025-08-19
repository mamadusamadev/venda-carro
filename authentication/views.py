from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from forms.auth_forms import LoginForm, RegisterForm
from service.auth_service import AuthService
from entities.user_entity import AuthCredentials, RegisterData


def login_view(request):
    """View para login de utilizadores com email"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    form = LoginForm()
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            credentials = AuthCredentials(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            
            success, user, message = AuthService.authenticate_user(credentials)
            
            if success and user:
                # Faz login do utilizador
                if AuthService.login_user(request, user):
                    messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
                    
                    # Redireciona para onde o utilizador queria ir ou dashboard
                    next_url = request.GET.get('next', 'dashboard:home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Erro ao fazer login. Tente novamente.')
            else:
                messages.error(request, message)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    
    context = {
        'form': form,
        'title': 'Entrar na Conta'
    }
    
    return render(request, 'authentication/login.html', context)


def register_view(request):
    """View para registo de utilizadores"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    form = RegisterForm()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            register_data = RegisterData(
                email=form.cleaned_data['email'],
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                password_confirm=form.cleaned_data['password_confirm'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                user_type=form.cleaned_data['user_type'],
                terms_accepted=form.cleaned_data['terms_accepted']
            )
            
            success, user, message = AuthService.register_user(register_data)
            
            if success:
                messages.success(request, message + ' Pode fazer login agora.')
                return redirect('authentication:login')
            else:
                messages.error(request, message)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    
    context = {
        'form': form,
        'title': 'Criar Conta'
    }
    
    return render(request, 'authentication/register.html', context)


@login_required
def logout_view(request):
    """View para logout"""
    if AuthService.logout_user(request):
        messages.success(request, 'Logout realizado com sucesso.')
    else:
        messages.error(request, 'Erro ao fazer logout.')
    
    return redirect('home')


@csrf_exempt
def check_username(request):
    """AJAX view para verificar se username existe"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        exists = AuthService.check_username_exists(username.lower().strip())
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})


@csrf_exempt
def check_email(request):
    """AJAX view para verificar se email existe"""
    if request.method == 'POST':
        email = request.POST.get('email', '')
        exists = AuthService.check_email_exists(email.lower().strip())
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})
