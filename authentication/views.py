from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from accounts.models import User, SellerProfile, BuyerProfile
import json

def login_view(request):
    """
    View para login de utilizadores
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                
                # Redirecionar para a página solicitada ou dashboard
                next_url = request.GET.get('next', reverse('dashboard:home'))
                return redirect(next_url)
            else:
                messages.error(request, 'Nome de utilizador ou palavra-passe incorretos.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
    
    return render(request, 'authentication/login.html')


def register_view(request):
    """
    View para registo de novos utilizadores
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        # Dados básicos
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type', 'buyer')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        district = request.POST.get('district')
        
        # Validações básicas
        if not all([username, email, password1, password2, first_name, last_name]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return render(request, 'authentication/register.html')
        
        if password1 != password2:
            messages.error(request, 'As palavras-passe não coincidem.')
            return render(request, 'authentication/register.html')
        
        if len(password1) < 6:
            messages.error(request, 'A palavra-passe deve ter pelo menos 6 caracteres.')
            return render(request, 'authentication/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de utilizador já existe.')
            return render(request, 'authentication/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está registado.')
            return render(request, 'authentication/register.html')
        
        try:
            # Criar utilizador
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                phone=phone,
                city=city,
                district=district
            )
            
            # Criar perfil específico
            if user_type == 'seller' or user_type == 'both':
                SellerProfile.objects.create(
                    user=user,
                    seller_type='individual',
                    address=request.POST.get('address', ''),
                    city=city or '',
                    district=district or '',
                    postal_code=request.POST.get('postal_code', ''),
                    description=request.POST.get('description', '')
                )
            
            if user_type == 'buyer' or user_type == 'both':
                BuyerProfile.objects.create(
                    user=user,
                    preferred_brands=request.POST.get('preferred_brands', ''),
                    max_budget=request.POST.get('max_budget') or None
                )
            
            # Fazer login automático
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Bem-vindo ao CarZone!')
            
            return redirect('dashboard:home')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    return render(request, 'authentication/register.html')


@login_required
def logout_view(request):
    """
    View para logout
    """
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'Até logo, {user_name}!')
    return redirect('home')


def check_username(request):
    """
    AJAX view para verificar se username já existe
    """
    if request.method == 'GET':
        username = request.GET.get('username')
        if username:
            exists = User.objects.filter(username=username).exists()
            return JsonResponse({'exists': exists})
    
    return JsonResponse({'exists': False})


def check_email(request):
    """
    AJAX view para verificar se email já existe
    """
    if request.method == 'GET':
        email = request.GET.get('email')
        if email:
            exists = User.objects.filter(email=email).exists()
            return JsonResponse({'exists': exists})
    
    return JsonResponse({'exists': False})
