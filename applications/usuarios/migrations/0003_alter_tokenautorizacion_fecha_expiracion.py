# Generated by Django 5.0.6 on 2024-09-27 17:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_tokenautorizacion_fecha_expiracion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenautorizacion',
            name='fecha_expiracion',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 28, 17, 16, 11, 246788, tzinfo=datetime.timezone.utc)),
        ),
    ]