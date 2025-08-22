from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from accounts.models import User
from django.db import IntegrityError


def cadastrar_user(user_entity):
    """Cadastrar um novo utilizador"""
    try:
        user = User.objects.create(
            username=user_entity.username,
            email=user_entity.email,
            password=make_password(user_entity.password),
            first_name=user_entity.first_name,
            last_name=user_entity.last_name,
            phone=user_entity.phone,
            user_type=user_entity.user_type,
            is_active=user_entity.is_active
        )
        return user
    except IntegrityError:
        return None


def autenticar_user(email, password):
    """Autenticar utilizador"""
    user = authenticate(username=email, password=password)
    return user


def fazer_login(request, user):
    """Fazer login do utilizador"""
    try:
        login(request, user)
        return True
    except Exception:
        return False


def fazer_logout(request):
    """Fazer logout do utilizador"""
    logout(request)


def listar_users():
    """Listar todos os utilizadores"""
    return User.objects.all()


def listar_user_id(id):
    """Buscar utilizador por ID"""
    try:
        return User.objects.get(id=id)
    except User.DoesNotExist:
        return None


def listar_user_email(email):
    """Buscar utilizador por email"""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def listar_user_username(username):
    """Buscar utilizador por username"""
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def verificar_email_existe(email):
    """Verificar se email já existe"""
    return User.objects.filter(email=email).exists()


def verificar_username_existe(username):
    """Verificar se username já existe"""
    return User.objects.filter(username=username).exists()


def editar_user(user_bd, user_entity):
    """Editar um utilizador existente"""
    user_bd.username = user_entity.username
    user_bd.email = user_entity.email
    user_bd.first_name = user_entity.first_name
    user_bd.last_name = user_entity.last_name
    user_bd.phone = user_entity.phone
    user_bd.user_type = user_entity.user_type
    user_bd.is_active = user_entity.is_active
    
    # Só atualiza password se foi fornecida nova
    if user_entity.password:
        user_bd.password = make_password(user_entity.password)
    
    user_bd.save(force_update=True)
    return user_bd


def ativar_user(user_bd):
    """Ativar utilizador"""
    user_bd.is_active = True
    user_bd.save(update_fields=['is_active'])
    return user_bd


def desativar_user(user_bd):
    """Desativar utilizador"""
    user_bd.is_active = False
    user_bd.save(update_fields=['is_active'])
    return user_bd


def remover_user(user_bd):
    """Remover um utilizador"""
    user_bd.delete()


def listar_vendedores():
    """Listar utilizadores vendedores"""
    return User.objects.filter(user_type='seller', is_active=True)


def listar_compradores():
    """Listar utilizadores compradores"""
    return User.objects.filter(user_type='buyer', is_active=True)


def contar_users_ativos():
    """Contar utilizadores ativos"""
    return User.objects.filter(is_active=True).count()


def contar_vendedores():
    """Contar vendedores"""
    return User.objects.filter(user_type='seller', is_active=True).count()


def contar_compradores():
    """Contar compradores"""
    return User.objects.filter(user_type='buyer', is_active=True).count() 