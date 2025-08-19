from typing import Optional


class UserEntity:
    """Entidade que representa um utilizador do sistema"""
    
    def __init__(self, user_id=None, email="", username="", first_name="", last_name="", 
                 phone="", user_type="buyer", is_active=True, is_verified=False):
        self.__id = user_id
        self.__email = email
        self.__username = username
        self.__first_name = first_name
        self.__last_name = last_name
        self.__phone = phone
        self.__user_type = user_type
        self.__is_active = is_active
        self.__is_verified = is_verified
        
        
        
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, user_id):
        self.__id = user_id
    
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, email):
        self.__email = email.lower().strip() if email else ""
    
    @property
    def username(self):
        return self.__username
    
    @username.setter
    def username(self, username):
        self.__username = username.lower().strip() if username else ""
    
    @property
    def first_name(self):
        return self.__first_name
    
    @first_name.setter
    def first_name(self, first_name):
        self.__first_name = first_name.strip() if first_name else ""
    
    @property
    def last_name(self):
        return self.__last_name
    
    @last_name.setter
    def last_name(self, last_name):
        self.__last_name = last_name.strip() if last_name else ""
    
    @property
    def phone(self):
        return self.__phone
    
    @phone.setter
    def phone(self, phone):
        self.__phone = phone.strip() if phone else ""
    
    @property
    def user_type(self):
        return self.__user_type
    
    @user_type.setter
    def user_type(self, user_type):
        valid_types = ['buyer', 'seller', 'both']
        if user_type in valid_types:
            self.__user_type = user_type
        else:
            self.__user_type = 'buyer'
    
    @property
    def is_active(self):
        return self.__is_active
    
    @is_active.setter
    def is_active(self, is_active):
        self.__is_active = bool(is_active)
    
    @property
    def is_verified(self):
        return self.__is_verified
    
    @is_verified.setter
    def is_verified(self, is_verified):
        self.__is_verified = bool(is_verified)
    
    def get_full_name(self):
        """Retorna o nome completo do utilizador"""
        return f"{self.__first_name} {self.__last_name}".strip()
    
    def is_seller(self):
        """Verifica se o utilizador é vendedor"""
        return self.__user_type in ['seller', 'both']
    
    def is_buyer(self):
        """Verifica se o utilizador é comprador"""
        return self.__user_type in ['buyer', 'both']


class AuthCredentials:
    """Entidade para credenciais de autenticação"""
    
    def __init__(self, email="", password=""):
        self.__email = email
        self.__password = password
    
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, email):
        self.__email = email.lower().strip() if email else ""
    
    @property
    def password(self):
        return self.__password
    
    @password.setter
    def password(self, password):
        self.__password = password


class RegisterData:
    """Entidade para dados de registo"""
    
    def __init__(self, email="", username="", password="", password_confirm="", 
                 first_name="", last_name="", phone="", user_type="buyer", terms_accepted=False):
        self.__email = email
        self.__username = username
        self.__password = password
        self.__password_confirm = password_confirm
        self.__first_name = first_name
        self.__last_name = last_name
        self.__phone = phone
        self.__user_type = user_type
        self.__terms_accepted = terms_accepted
    
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, email):
        self.__email = email.lower().strip() if email else ""
    
    @property
    def username(self):
        return self.__username
    
    @username.setter
    def username(self, username):
        self.__username = username.lower().strip() if username else ""
    
    @property
    def password(self):
        return self.__password
    
    @password.setter
    def password(self, password):
        self.__password = password
    
    @property
    def password_confirm(self):
        return self.__password_confirm
    
    @password_confirm.setter
    def password_confirm(self, password_confirm):
        self.__password_confirm = password_confirm
    
    @property
    def first_name(self):
        return self.__first_name
    
    @first_name.setter
    def first_name(self, first_name):
        self.__first_name = first_name.strip() if first_name else ""
    
    @property
    def last_name(self):
        return self.__last_name
    
    @last_name.setter
    def last_name(self, last_name):
        self.__last_name = last_name.strip() if last_name else ""
    
    @property
    def phone(self):
        return self.__phone
    
    @phone.setter
    def phone(self, phone):
        self.__phone = phone.strip() if phone else ""
    
    @property
    def user_type(self):
        return self.__user_type
    
    @user_type.setter
    def user_type(self, user_type):
        valid_types = ['buyer', 'seller', 'both']
        if user_type in valid_types:
            self.__user_type = user_type
        else:
            self.__user_type = 'buyer'
    
    @property
    def terms_accepted(self):
        return self.__terms_accepted
    
    @terms_accepted.setter
    def terms_accepted(self, terms_accepted):
        self.__terms_accepted = bool(terms_accepted) 