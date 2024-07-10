from django.db import models

# Create your models here.
class Cat001Estado(models.Model):
    nombre = models.TextField()
    sigla = models.TextField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'cat_001_estado'

        verbose_name = 'ESTADO'
        verbose_name_plural = 'ESTADOS'

class Cat004Ciudad(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    nombre = models.TextField()
    departamento_id_003 = models.IntegerField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'cat_004_ciudad'

        verbose_name = 'CIUDAD'
        verbose_name_plural = 'CIUDADES'