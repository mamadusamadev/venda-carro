from typing import Optional, Tuple
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from entities.user_entity import UserEntity, AuthCredentials, RegisterData
from accounts.models import SellerProfile, BuyerProfile

User = get_user_model()


class EmailBackend(ModelBackend):
    """Backend personalizado para autenticação por email"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Tenta encontrar o utilizador pelo email
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None


class AuthService:
    """Service responsável pela autenticação e gestão de utilizadores"""
    
    @staticmethod
    def authenticate_user(credentials: AuthCredentials) -> Tuple[bool, Optional[User], str]:
        """
        Autentica um utilizador usando email e password
        
        Returns:
            Tuple[bool, Optional[User], str]: (sucesso, utilizador, mensagem)
        """
        try:
            # Usa o backend personalizado para autenticação por email
            backend = EmailBackend()
            user = backend.authenticate(None, username=credentials.email, password=credentials.password)
            
            if user is not None:
                if user.is_active:
                    return True, user, "Login realizado com sucesso"
                else:
                    return False, None, "Conta desativada. Contacte o administrador."
            else:
                return False, None, "Email ou palavra-passe incorretos"
                
        except Exception as e:
            return False, None, f"Erro no login: {str(e)}"
    
    @staticmethod
    def login_user(request, user: User) -> bool:
        """
        Faz login do utilizador na sessão
        
        Args:
            request: HttpRequest
            user: Utilizador a fazer login
            
        Returns:
            bool: True se sucesso
        """
        try:
            login(request, user)
            return True
        except Exception:
            return False
    
    @staticmethod
    def logout_user(request) -> bool:
        """
        Faz logout do utilizador
        
        Args:
            request: HttpRequest
            
        Returns:
            bool: True se sucesso
        """
        try:
            logout(request)
            return True
        except Exception:
            return False
    
    @staticmethod
    def register_user(register_data: RegisterData) -> Tuple[bool, Optional[User], str]:
        """
        Regista um novo utilizador
        
        Args:
            register_data: Dados do registo
            
        Returns:
            Tuple[bool, Optional[User], str]: (sucesso, utilizador, mensagem)
        """
        try:
            # Validações
            if register_data.password != register_data.password_confirm:
                return False, None, "As palavras-passe não coincidem"
            
            if User.objects.filter(email=register_data.email).exists():
                return False, None, "Já existe uma conta com este email"
            
            if User.objects.filter(username=register_data.username).exists():
                return False, None, "Já existe uma conta com este nome de utilizador"
            
            if not register_data.terms_accepted:
                return False, None, "Deve aceitar os termos e condições"
            
            # Valida a palavra-passe
            try:
                validate_password(register_data.password)
            except ValidationError as e:
                return False, None, " ".join(e.messages)
            
            # Cria o utilizador numa transação
            with transaction.atomic():
                user = User.objects.create_user(
                    username=register_data.username,
                    email=register_data.email,
                    password=register_data.password,
                    first_name=register_data.first_name,
                    last_name=register_data.last_name,
                    phone=register_data.phone,
                    user_type=register_data.user_type
                )
                
                # Cria perfis baseados no tipo de utilizador
                if register_data.user_type in ['buyer', 'both']:
                    BuyerProfile.objects.create(user=user)
                
                if register_data.user_type in ['seller', 'both']:
                    SellerProfile.objects.create(user=user)
                
                return True, user, "Conta criada com sucesso"
                
        except Exception as e:
            return False, None, f"Erro ao criar conta: {str(e)}"
    
    @staticmethod
    def check_email_exists(email: str) -> bool:
        """Verifica se o email já existe"""
        return User.objects.filter(email=email).exists()
    
    @staticmethod
    def check_username_exists(username: str) -> bool:
        """Verifica se o username já existe"""
        return User.objects.filter(username=username).exists()
    
    @staticmethod
    def get_user_entity(user: User) -> UserEntity:
        """Converte um User model para UserEntity"""
        return UserEntity(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            user_type=user.user_type,
            is_active=user.is_active,
            is_verified=user.is_verified
        ) 