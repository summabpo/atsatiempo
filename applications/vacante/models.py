from django.db import models
from applications.common.models import Cat001Estado, Cat004Ciudad

# Create your models here.
class SoftSkill(models.Model):
    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class HardSkill(models.Model):
    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class ProfesionEstudio(models.Model):
    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

class Vacante(models.Model):
    ESTADO_VACANTE = [
        (1, 'Abierto'),
        (2, 'Cerrado'),
    ]

    titulo = models.CharField(max_length=200)
    numero_posiciones = models.IntegerField()
    profesion_estudio = models.ForeignKey(ProfesionEstudio, on_delete=models.CASCADE)
    experiencia_requerida = models.TextField()
    soft_skills = models.ManyToManyField(SoftSkill)
    hard_skills = models.ManyToManyField(HardSkill)
    funciones_responsabilidades = models.TextField()
    ciudad = models.ForeignKey(Cat004Ciudad, on_delete=models.CASCADE)
    salario = models.IntegerField(null=True, blank=True)  # Opcional
    estado_vacante = models.IntegerField(choices=ESTADO_VACANTE, default=1)

    def __str__(self):
        return self.titulo