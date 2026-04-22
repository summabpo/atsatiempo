# Generated manually: Cli087ReporteAccionDecisivaReclutado.fecha_actualizacion + usuario_actualizado

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
from django.db.models import F


def forwards_copiar_usuario_y_fecha(apps, schema_editor):
    Model = apps.get_model("reclutado", "Cli087ReporteAccionDecisivaReclutado")
    Model.objects.all().update(
        usuario_actualizado_id=F("usuario_cargado_id"),
        fecha_actualizacion=F("fecha_cargado"),
    )


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reclutado", "0019_cli087reporteacciondecisivareclutado_estado_accion_decisiva"),
    ]

    operations = [
        migrations.AddField(
            model_name="cli087reporteacciondecisivareclutado",
            name="fecha_actualizacion",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="cli087reporteacciondecisivareclutado",
            name="usuario_actualizado",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reportes_accion_decisiva_actualizados",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(forwards_copiar_usuario_y_fecha, backwards_noop),
        migrations.AlterField(
            model_name="cli087reporteacciondecisivareclutado",
            name="usuario_actualizado",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reportes_accion_decisiva_actualizados",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="cli087reporteacciondecisivareclutado",
            name="fecha_actualizacion",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
