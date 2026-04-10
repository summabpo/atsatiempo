# Reemplaza cliente por cargo en la asignación acciones decisivas; renombra modelo y tabla.
# Se vacían filas existentes: la relación anterior era por cliente y no se puede mapear 1:1 a cargo.

import django.db.models.deletion
from django.db import migrations, models


def _vaciar_asignaciones_acciones_decisivas(apps, schema_editor):
    Model = apps.get_model('cliente', 'Cli086AsignacionClienteAccionesDecisivas')
    Model.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0023_cli085_acciones_decisivas_cli086_asignacion_cliente_acciones_decisivas'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(_vaciar_asignaciones_acciones_decisivas, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='cli086asignacionclienteaccionesdecisivas',
            name='cliente',
        ),
        migrations.AddField(
            model_name='cli086asignacionclienteaccionesdecisivas',
            name='cargo',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='cliente.cli068cargo',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='cli086asignacionclienteaccionesdecisivas',
            unique_together={('cargo', 'accion_decisiva')},
        ),
        migrations.RenameModel(
            old_name='Cli086AsignacionClienteAccionesDecisivas',
            new_name='Cli086AsignacionCargoAccionesDecisivas',
        ),
        migrations.AlterModelTable(
            name='Cli086AsignacionCargoAccionesDecisivas',
            table='cli_086_asignacion_cargo_acciones_decisivas',
        ),
    ]
