# Generated by Django 5.0.6 on 2024-12-30 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacante', '0016_cli052vacante_usuario_asignado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cli052vacante',
            name='experiencia_requerida',
            field=models.IntegerField(choices=[(1, '0 a 6 Meses'), (2, '1 año a 2 años'), (3, '2 años de 3 años'), (4, 'Sin Experiencia'), (5, '3 años de 4 años'), (6, '4 años de 5 años'), (7, '5 años de 6 años'), (8, '6 años de 7 años'), (9, '7 años de 8 años'), (10, '8 años de 9 años'), (11, '9 años de 10 años'), (12, '10 años o más')]),
        ),
    ]
