# Generated by Django 5.0.6 on 2025-04-22 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_usuariobase_imagen_perfil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuariobase',
            name='imagen_perfil',
            field=models.ImageField(blank=True, null=True, upload_to='media_uploads/usuario/', verbose_name='Imagen de Perfil Usuario'),
        ),
    ]
