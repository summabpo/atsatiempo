from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Grupo(models.Model):
    name = models.CharField(max_length=255, unique=True)
    activate = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

class UsuarioBase(AbstractUser):
    primer_nombre    = models.CharField(max_length=15, blank=True)
    segundo_nombre   = models.CharField(max_length=15, blank=True)
    primer_apellido  = models.CharField(max_length=15, blank=True)
    segundo_apellido = models.CharField(max_length=15, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    is_verificado = models.BooleanField(default=False)
    group = models.ForeignKey(Grupo, on_delete=models.CASCADE)

    def __str__(self):
        return self.username
