from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Serviço para envio de emails relacionados ao sistema de compras
    """
    
    @staticmethod
    def send_purchase_request_notification(purchase_request):
        """
        Enviar email de notificação de nova solicitação de compra para o vendedor
        """
        try:
            subject = f'Nova Solicitação de Compra - {purchase_request.car.brand.name} {purchase_request.car.car_model.name}'
            
            # Contexto para o template
            context = {
                'purchase_request': purchase_request,
                'seller': purchase_request.seller,
                'car': purchase_request.car,
                'site_url': settings.SITE_URL,
            }
            
            # Renderizar template HTML
            html_message = render_to_string('emails/purchase_request_notification.html', context)
            plain_message = strip_tags(html_message)
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[purchase_request.seller.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Email de solicitação de compra enviado para {purchase_request.seller.email}')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao enviar email de solicitação de compra: {str(e)}')
            return False
    
    @staticmethod
    def send_purchase_notification(purchase):
        """
        Enviar email de notificação de nova compra direta para o vendedor
        """
        try:
            subject = f'Nova Compra Realizada - {purchase.car.brand.name} {purchase.car.car_model.name}'
            
            # Contexto para o template
            context = {
                'purchase': purchase,
                'seller': purchase.seller,
                'car': purchase.car,
                'site_url': settings.SITE_URL,
            }
            
            # Renderizar template HTML
            html_message = render_to_string('emails/purchase_notification.html', context)
            plain_message = strip_tags(html_message)
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[purchase.seller.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Email de compra enviado para {purchase.seller.email}')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao enviar email de compra: {str(e)}')
            return False
    
    @staticmethod
    def send_purchase_request_response(purchase_request):
        """
        Enviar email para o comprador quando o vendedor responder à solicitação
        """
        try:
            if purchase_request.status == 'accepted':
                subject = f'Solicitação Aceite - {purchase_request.car.brand.name} {purchase_request.car.car_model.name}'
                template = 'emails/purchase_request_accepted.html'
            elif purchase_request.status == 'rejected':
                subject = f'Solicitação Rejeitada - {purchase_request.car.brand.name} {purchase_request.car.car_model.name}'
                template = 'emails/purchase_request_rejected.html'
            else:
                subject = f'Atualização da Solicitação - {purchase_request.car.brand.name} {purchase_request.car.car_model.name}'
                template = 'emails/purchase_request_update.html'
            
            # Contexto para o template
            context = {
                'purchase_request': purchase_request,
                'buyer': purchase_request.buyer,
                'car': purchase_request.car,
                'site_url': settings.SITE_URL,
            }
            
            # Renderizar template HTML
            html_message = render_to_string(template, context)
            plain_message = strip_tags(html_message)
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[purchase_request.buyer_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Email de resposta de solicitação enviado para {purchase_request.buyer_email}')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao enviar email de resposta de solicitação: {str(e)}')
            return False
    
    @staticmethod
    def send_purchase_status_update(purchase, old_status, new_status):
        """
        Enviar email de atualização de status de compra para o comprador
        """
        try:
            subject = f'Atualização da Compra - {purchase.car.brand.name} {purchase.car.car_model.name}'
            
            # Contexto para o template
            context = {
                'purchase': purchase,
                'buyer': purchase.buyer,
                'car': purchase.car,
                'old_status': old_status,
                'new_status': new_status,
                'site_url': settings.SITE_URL,
            }
            
            # Renderizar template HTML
            html_message = render_to_string('emails/purchase_status_update.html', context)
            plain_message = strip_tags(html_message)
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[purchase.buyer_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Email de atualização de status enviado para {purchase.buyer_email}')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao enviar email de atualização de status: {str(e)}')
            return False
    
    @staticmethod
    def send_purchase_confirmation(purchase):
        """
        Enviar email de confirmação de compra para o comprador
        """
        try:
            subject = f'Confirmação de Compra - {purchase.car.brand.name} {purchase.car.car_model.name}'
            
            # Contexto para o template
            context = {
                'purchase': purchase,
                'buyer': purchase.buyer,
                'car': purchase.car,
                'site_url': settings.SITE_URL,
            }
            
            # Renderizar template HTML
            html_message = render_to_string('emails/purchase_confirmation.html', context)
            plain_message = strip_tags(html_message)
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[purchase.buyer_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Email de confirmação de compra enviado para {purchase.buyer_email}')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao enviar email de confirmação de compra: {str(e)}')
            return False
