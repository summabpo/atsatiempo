from django.contrib.auth.models import AbstractUser
from django.db import models
from applications.cliente.models import Cli051Cliente
# Create your models here.
class Grupo(models.Model):
    name = models.CharField(max_length=255, unique=True)
    activate = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)

    class Meta:
        #managed = False
        db_table = 'grupo'

        verbose_name = 'GRUPO'
        verbose_name_plural = 'GRUPOS'

class UsuarioBase(AbstractUser):
    primer_nombre    = models.CharField(max_length=15, blank=True)
    segundo_nombre   = models.CharField(max_length=15, blank=True)
    primer_apellido  = models.CharField(max_length=15, blank=True)
    segundo_apellido = models.CharField(max_length=15, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    is_verificado = models.BooleanField(default=False)
    group = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    cliente_id_051 = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE, null=True)
    
    def str(self):
        return self.username
    class Meta:
        #managed = False
        db_table = 'usuario'

        verbose_name = 'USUARIO'
        verbose_name_plural = 'USUARIOS'