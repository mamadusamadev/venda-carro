from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cars.models_chat import ChatRoom


class Command(BaseCommand):
    help = 'Verifica e fecha chats inativos (comprador sem resposta por 5+ minutos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quais chats seriam fechados sem efetivamente fechá-los',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Buscar chats ativos com compradores inativos
        now = timezone.now()
        inactive_threshold = now - timedelta(minutes=5)
        
        # Chats onde o comprador está inativo há mais de 5 minutos
        inactive_chats = ChatRoom.objects.filter(
            status='active',
            buyer_last_activity__lt=inactive_threshold,
            buyer_last_activity__isnull=False
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Encontrados {inactive_chats.count()} chats inativos')
        )
        
        if dry_run:
            for chat in inactive_chats:
                time_diff = now - chat.buyer_last_activity
                self.stdout.write(
                    f'  - Chat {chat.id}: {chat.buyer.username} inativo há {time_diff}'
                )
            return
        
        # Fechar chats inativos
        closed_count = 0
        for chat in inactive_chats:
            try:
                time_diff = now - chat.buyer_last_activity
                self.stdout.write(
                    f'Fechando chat {chat.id}: {chat.buyer.username} inativo há {time_diff}'
                )
                chat.auto_close_for_inactivity()
                closed_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao fechar chat {chat.id}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Fechados {closed_count} chats por inatividade')
        )
