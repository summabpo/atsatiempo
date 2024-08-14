from django.db import models
from applications.common.models import Cat001Estado, Cat004Ciudad
# Create your models here.
class Cli051Cliente(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    nit = models.IntegerField(blank=False)
    razon_social = models.CharField(max_length=100, blank=False)
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004')
    email = models.EmailField(unique=True)
    contacto = models.CharField(max_length=50, blank=False)
    telefono = models.CharField(max_length=20, blank=False)
    perfil_empresarial = models.TextField(blank=True)  # Nuevo campo de texto
    logo = models.ImageField(upload_to='cliente', blank=True, null=True)  # Nuevo campo de imagen

    def __str__(self):
        return self.razon_social + ' - ' + self.nit
    class Meta:
        
        db_table = 'cli_051_cliente'

        verbose_name = 'CLIENTE'
        verbose_name_plural = 'CLIENTES'