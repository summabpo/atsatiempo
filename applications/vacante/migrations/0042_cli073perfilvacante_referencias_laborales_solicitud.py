# Generated manually for Cli073PerfilVacante.referencias_laborales_solicitud

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vacante", "0041_cli052vacante_requerimientos_especiales_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cli073perfilvacante",
            name="referencias_laborales_solicitud",
            field=models.JSONField(
                blank=True,
                help_text="Referencias laborales solicitadas en la vacante (lista de {orden, descripcion})",
                null=True,
            ),
        ),
    ]
