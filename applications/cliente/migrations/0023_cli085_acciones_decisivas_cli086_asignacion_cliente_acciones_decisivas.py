# Generated manually for Cli085 / Cli086

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0022_remove_cli051clientepoliticas_respuestas_politica_and_more'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cli085AccionesDecisivas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('fecha_cargue', models.DateTimeField(auto_now_add=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('estado', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='common.cat001estado')),
            ],
            options={
                'verbose_name': 'ACCION DECISIVA',
                'verbose_name_plural': 'ACCIONES DECISIVAS',
                'db_table': 'cli_085_acciones_decisivas',
            },
        ),
        migrations.CreateModel(
            name='Cli086AsignacionClienteAccionesDecisivas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateField(auto_now_add=True)),
                ('accion_decisiva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cliente.cli085accionesdecisivas')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cliente.cli051cliente')),
                ('estado', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='common.cat001estado')),
            ],
            options={
                'verbose_name': 'ASIGNACION CLIENTE ACCION DECISIVA',
                'verbose_name_plural': 'ASIGNACIONES CLIENTE ACCIONES DECISIVAS',
                'db_table': 'cli_086_asignacion_cliente_acciones_decisivas',
                'unique_together': {('cliente', 'accion_decisiva')},
            },
        ),
    ]
