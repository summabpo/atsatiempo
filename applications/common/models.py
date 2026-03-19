from django.db import models

# UsuarioBase y Grupo se referencian como strings para evitar importación circular
# (usuarios -> cliente -> common -> usuarios)
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


class Cat005AsignacionQr(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)
    usuario_asignado = models.ForeignKey('usuarios.UsuarioBase', models.DO_NOTHING, db_column='usuario_asignado')
    grupo_asignacion = models.ForeignKey('usuarios.Grupo', models.DO_NOTHING, db_column='grupo_asignacion')
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    token_qr = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):

        return self.nombre
    class Meta:
        db_table = 'cat_005_asignacion_qr'
        verbose_name = 'ASIGNACION_QR'
        verbose_name_plural = 'ASIGNACIONES_QR'