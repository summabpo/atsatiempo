# Generated by Django 5.0.6 on 2024-08-06 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidato', '0003_alter_can102experiencia_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='can102experiencia',
            name='cargo',
            field=models.CharField(default='Sin especificar', max_length=100),
        ),
    ]