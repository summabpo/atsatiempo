from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from applications.cliente.models import Cli051Cliente
from applications.candidato.models import Can101Candidato
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
    
    @classmethod
    def obtener_nombres(cls):
        return list(cls.objects.values_list('nombre', flat=True))

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
    candidato_id_101 = models.ForeignKey(Can101Candidato, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuario')

    # Sobrescribimos estos campos para evitar conflictos
    groups = None
    user_permissions = None
    
    def str(self):
        return self.username
    class Meta:
        #managed = False
        db_table = 'usuario'

        verbose_name = 'USUARIO'
        verbose_name_plural = 'USUARIOS'
    
    def has_perm(self, perm, obj=None):
        # Implementa aquí tu lógica personalizada o simplemente:
        return True  # O False, dependiendo de tu caso de uso

    def has_perms(self, perm_list, obj=None):
        # Puedes implementar tu lógica aquí o:
        return all(self.has_perm(perm) for perm in perm_list)

class TokenAutorizacion(models.Model):
    user = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, null=True, blank=True)
    token = models.CharField(max_length=255, unique=True)
    fecha_expiracion = models.DateTimeField(default=timezone.now() + timedelta(days=1))
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'token_autorizacion'

        verbose_name = 'TOKEN AUTORIZACION'