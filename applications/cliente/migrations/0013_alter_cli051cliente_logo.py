# Generated by Django 5.0.6 on 2025-04-16 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0012_alter_cli051cliente_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cli051cliente',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='cliente/'),
        ),
    ]
