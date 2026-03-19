# Generated manually - agrega qr_code y token_qr a Cat005AsignacionQr

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_cat005asignacionqr'),
    ]

    operations = [
        migrations.AddField(
            model_name='cat005asignacionqr',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='qr_codes/'),
        ),
        migrations.AddField(
            model_name='cat005asignacionqr',
            name='token_qr',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
