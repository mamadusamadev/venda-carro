from cars.models_purchase import Notification


def notifications_count(request):
    """
    Context processor para adicionar o contador de notificações não lidas
    em todos os templates do dashboard
    """
    unread_count = 0
    
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    
    return {
        'unread_notifications_count': unread_count
    }
