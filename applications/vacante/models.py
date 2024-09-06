from django.db import models
from applications.common.models import Cat001Estado, Cat004Ciudad

# Create your models here.
class Cli053SoftSkill(models.Model):
    nombre = models.CharField(max_length=200)
    estado_id_004 = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Cli054HardSkill(models.Model):
    nombre = models.CharField(max_length=200)
    estado_id_004 = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class Cli055ProfesionEstudio(models.Model):
    nombre = models.CharField(max_length=200)
    estado_id_004 = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

class Cli052Vacante(models.Model):
    ESTADO_VACANTE = [
        (1, 'Abierta'),
        (2, 'Cerrada'),
        (3, 'Cancelada'),
    ]

    titulo = models.CharField(max_length=200)
    numero_posiciones = models.IntegerField()
    profesion_estudio_id_055 = models.ForeignKey(Cli055ProfesionEstudio, on_delete=models.CASCADE)
    experiencia_requerida = models.TextField()
    soft_skills_id_053 = models.ManyToManyField(Cli053SoftSkill)
    hard_skills_id_054 = models.ManyToManyField(Cli054HardSkill)
    funciones_responsabilidades = models.TextField()
    ciudad = models.ForeignKey(Cat004Ciudad, on_delete=models.CASCADE)
    salario = models.IntegerField(null=True, blank=True)  # Opcional
    estado_vacante = models.IntegerField(choices=ESTADO_VACANTE, default=1)
    estado_id_004 = models.ForeignKey(Cat001Estado, models.DO_NOTHING)

    def __str__(self):
        return self.titulo