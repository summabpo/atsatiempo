# Generated by Django 5.0.6 on 2025-03-14 14:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacante', '0018_remove_cli052vacante_ciudad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cli052vacante',
            name='perfil_vacante',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vacante.cli073perfilvacante'),
        ),
    ]
