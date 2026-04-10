# Alinea BD con modelo Cli085AccionesDecisivas (cantidad_dias_gestion).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0025_cli051cliente_cantidad_dias_envio_candidatos'),
    ]

    operations = [
        migrations.AddField(
            model_name='cli085accionesdecisivas',
            name='cantidad_dias_gestion',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
