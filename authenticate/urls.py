
# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    HomeView, BuyerRegistrationView, SellerRegistrationView,
    BuyerDashboardView, SellerDashboardView
)

urlpatterns = [
    # Página inicial
    path('', HomeView.as_view(), name='home'),
    
    # Registro
    path('registro/comprador/', BuyerRegistrationView.as_view(), name='buyer_register'),
    path('registro/vendedor/', SellerRegistrationView.as_view(), name='seller_register'),
    
    # Login/Logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboards
    path('dashboard/comprador/', BuyerDashboardView.as_view(), name='buyer_dashboard'),
    path('dashboard/vendedor/', SellerDashboardView.as_view(), name='seller_dashboard'),
    
    # Reset de senha
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
]