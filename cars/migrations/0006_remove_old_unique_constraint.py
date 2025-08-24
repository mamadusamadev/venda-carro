# Generated migration to manually remove old unique constraint

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0005_alter_chatroom_unique_together_and_more'),
    ]

    operations = [
        # Remover constraint antiga manualmente se ainda existir
        migrations.RunSQL(
            "DROP INDEX IF EXISTS cars_chatroom_car_id_buyer_id_e959a315_uniq;",
            reverse_sql="-- Não é possível recriar a constraint antiga"
        ),
        migrations.RunSQL(
            "ALTER TABLE cars_chatroom DROP CONSTRAINT IF EXISTS cars_chatroom_car_id_buyer_id_e959a315_uniq;",
            reverse_sql="-- Não é possível recriar a constraint antiga"
        ),
    ]
