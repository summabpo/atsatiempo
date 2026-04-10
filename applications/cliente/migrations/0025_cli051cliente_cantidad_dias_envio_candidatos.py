# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0024_cli086_cargo_acciones_decisivas'),
    ]

    operations = [
        migrations.AddField(
            model_name='cli051cliente',
            name='cantidad_dias_envio_candidatos',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
