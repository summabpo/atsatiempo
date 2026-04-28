# Generated manually: create Cli087ReporteAccionDecisivaReclutado base model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cliente", "0023_cli085_acciones_decisivas_cli086_asignacion_cliente_acciones_decisivas"),
        ("common", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reclutado", "0018_cli084asignacionregistroreclutado"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cli087ReporteAccionDecisivaReclutado",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "archivo_reporte",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="media_uploads/reporte_accion_decisiva/",
                        verbose_name="Reporte Acción Decisiva",
                    ),
                ),
                ("fecha_cargado", models.DateTimeField(auto_now_add=True, verbose_name="Fecha de cargado")),
                ("json_data", models.JSONField(blank=True, null=True, verbose_name="Datos del reporte")),
                (
                    "accion_decisiva",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportes_accion_decisiva",
                        to="cliente.cli085accionesdecisivas",
                    ),
                ),
                (
                    "aplicacion_vacante_056",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportes_accion_decisiva",
                        to="reclutado.cli056aplicacionvacante",
                    ),
                ),
                (
                    "estado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportes_accion_decisiva",
                        to="common.cat001estado",
                    ),
                ),
                (
                    "usuario_cargado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportes_accion_decisiva_cargados",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "cli_087_reporte_accion_decisiva_reclutado",
                "verbose_name": "REPORTE ACCIÓN DECISIVA RECLUTADO",
                "verbose_name_plural": "REPORTES ACCIÓN DECISIVA RECLUTADO",
            },
        ),
    ]

