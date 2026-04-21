# Generated manually for Cli087ReporteAccionDecisivaReclutado.estado_accion_decisiva

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reclutado', '0018_cli084asignacionregistroreclutado'),
    ]

    operations = [
        migrations.AddField(
            model_name='cli087reporteacciondecisivareclutado',
            name='estado_accion_decisiva',
            field=models.CharField(
                choices=[
                    ('aprobada', 'Aprobada'),
                    ('pendiente', 'Pendiente'),
                    ('no_aprobada', 'No aprobada'),
                ],
                default='pendiente',
                max_length=20,
                verbose_name='Estado Acción Decisiva',
            ),
        ),
    ]
