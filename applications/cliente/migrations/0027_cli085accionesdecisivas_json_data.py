# Campo json_data para catálogo de acciones decisivas (API config/decisiones).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0026_cli085accionesdecisivas_cantidad_dias_gestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='cli085accionesdecisivas',
            name='json_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
