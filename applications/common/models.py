from django.db import models

# Create your models here.
class Cat001Estado(models.Model):
    nombre = models.CharField(max_length=30)
    sigla = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        #managed = False
        db_table = 'cat_001_estado'

        verbose_name = 'ESTADO'
        verbose_name_plural = 'ESTADOS'

class Cat004Ciudad(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    nombre = models.CharField(max_length=50)
    departamento_id_003 = models.IntegerField(blank=True, null=True)

    def __str__(self):
            return self.nombre
    class Meta:
        #managed = False
        db_table = 'cat_004_ciudad'

        verbose_name = 'CIUDAD'
        verbose_name_plural = 'CIUDADES'