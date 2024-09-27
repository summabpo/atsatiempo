# Generated by Django 5.0.6 on 2024-09-25 14:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cli051Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nit', models.IntegerField()),
                ('razon_social', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('contacto', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=20)),
                ('perfil_empresarial', models.TextField(blank=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='cliente')),
                ('ciudad_id_004', models.ForeignKey(db_column='ciudad_id_004', on_delete=django.db.models.deletion.DO_NOTHING, to='common.cat004ciudad')),
                ('estado_id_001', models.ForeignKey(db_column='estado_id_001', on_delete=django.db.models.deletion.DO_NOTHING, to='common.cat001estado')),
            ],
            options={
                'verbose_name': 'CLIENTE',
                'verbose_name_plural': 'CLIENTES',
                'db_table': 'cli_051_cliente',
            },
        ),
    ]