
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from forms.users_form import BuyerRegistrationForm, SellerRegistrationForm
from .models import User, Car



class BuyerRegistrationView(CreateView):
    """
    Registro para compradores
    """
    model = User
    form_class = BuyerRegistrationForm
    template_name = 'registration/buyer_register.html'
    success_url = reverse_lazy('buyer_dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request, 
            'Cadastro realizado com sucesso! Bem-vindo à nossa plataforma!'
        )
        return response


class SellerRegistrationView(CreateView):
    """
    Registro para vendedores
    """
    model = User
    form_class = SellerRegistrationForm
    template_name = 'registration/seller_register.html'
    success_url = reverse_lazy('seller_dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request, 
            'Cadastro realizado com sucesso! Sua conta de vendedor foi criada!'
        )
        return response


@method_decorator(login_required, name='dispatch')
class BuyerDashboardView(TemplateView):
    """
    Dashboard do comprador
    """
    template_name = 'dashboard/buyer_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_buy():
            messages.error(request, 'Acesso negado. Você não tem permissão de comprador.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'user_profile': getattr(user, 'buyer_profile', None),
            'favorite_cars': user.favorites.select_related('car')[:5] if hasattr(user, 'favorites') else [],
            'recommended_cars': Car.objects.filter(status='available')[:6],
            'recent_views': [],  # Implementar histórico de visualizações
        })
        return context


@method_decorator(login_required, name='dispatch')
class SellerDashboardView(TemplateView):
    """
    Dashboard do vendedor
    """
    template_name = 'dashboard/seller_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_sell():
            messages.error(request, 'Acesso negado. Você não tem permissão de vendedor.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'seller_profile': getattr(user, 'seller_profile', None),
            'my_cars': user.cars_for_sale.all()[:10],
            'total_cars': user.cars_for_sale.count(),
            'available_cars': user.cars_for_sale.filter(status='available').count(),
            'sold_cars': user.cars_for_sale.filter(status='sold').count(),
            'recent_views': 0,  # Implementar estatísticas
        })
        return context
