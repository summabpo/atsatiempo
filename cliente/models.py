from django.db import models
from common.models import Cat001Estado, Cat004Ciudad
# Create your models here.
class Cli051Cliente(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    nit = models.IntegerField()
    razon_social = models.TextField()
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004')
    email = models.EmailField(unique=True)

    class Meta:
        managed = False
        db_table = 'cli_051_cliente'

        verbose_name = 'CLIENTE'
        verbose_name_plural = 'CLIENTES'