# Generated by Django 5.0.6 on 2024-10-23 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacante', '0006_alter_cli052vacante_estado_vacante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cli056aplicacionvacante',
            name='estado_aplicacion',
            field=models.IntegerField(choices=[(1, 'Aplicado'), (2, 'Entrevista Programada'), (3, 'Entrevista Aprobada'), (4, 'Entrevista No Aprobada'), (5, 'Prueba Programada'), (6, 'Prueba Superada'), (7, 'Prueba No Superada'), (8, 'Seleccionado'), (9, 'Finalizada'), (10, 'Cancelada'), (11, 'Desiste')], default=1),
        ),
    ]
