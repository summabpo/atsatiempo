from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from applications.cliente.models import Cli051Cliente
# Create your models here.

class Permiso(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        db_table = 'permiso'
        verbose_name = 'PERMISO'
        verbose_name_plural = 'PERMISOS'

    def __str__(self):
        return self.nombre

class Grupo(models.Model):
    name = models.CharField(max_length=255)
    activate = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)

    class Meta:
        #managed = False
        db_table = 'grupo'

        verbose_name = 'GRUPO'
        verbose_name_plural = 'GRUPOS'

class GrupoPermiso(models.Model):
    grupo = models.ForeignKey('Grupo', on_delete=models.CASCADE, related_name='grupo_permisos')
    permiso = models.ForeignKey('Permiso', on_delete=models.CASCADE, related_name='grupo_permisos')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'grupo_permiso'
        unique_together = ('grupo', 'permiso')
        verbose_name = 'ASIGNACIÓN DE PERMISO A GRUPO'
        verbose_name_plural = 'ASIGNACIONES DE PERMISOS A GRUPOS'

    def __str__(self):
        return f"{self.grupo.name} - {self.permiso.nombre} ({self.fecha})"

class UsuarioBase(AbstractUser):
    primer_nombre    = models.CharField(max_length=15, blank=True)
    segundo_nombre   = models.CharField(max_length=15, blank=True)
    primer_apellido  = models.CharField(max_length=15, blank=True)
    segundo_apellido = models.CharField(max_length=15, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    is_verificado = models.BooleanField(default=False)
    group = models.ForeignKey(Grupo, on_delete=models.CASCADE, null=True, blank=True)
    cliente_id_051 = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE, null=True)
    
    def str(self):
        return self.username
    class Meta:
        #managed = False
        db_table = 'usuario'

        verbose_name = 'USUARIO'
        verbose_name_plural = 'USUARIOS'

class TokenAutorizacion(models.Model):
    user = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE, null=True, blank=True)
    token = models.CharField(max_length=255, unique=True)
    fecha_expiracion = models.DateTimeField(default=timezone.now() + timedelta(days=1))
    class Meta:
        db_table = 'token_autorizacion'

        verbose_name = 'TOKEN AUTORIZACION'
    