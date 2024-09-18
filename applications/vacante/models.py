from django.db import models
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.cliente.models import Cli051Cliente
from applications.candidato.models import Can101Candidato

# Create your models here.
class Cli053SoftSkill(models.Model):
    nombre = models.CharField(max_length=200)
    estado_id_001 = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
    class Meta:
        #managed = False
        db_table = 'cli_053_soft_skill'

        verbose_name = 'SOFT_SKILL'

class Cli054HardSkill(models.Model):
    nombre = models.CharField(max_length=200)
    estado_id_001 = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
    class Meta:
        #managed = False
        db_table = 'cli_054_hard_skill'

        verbose_name = 'HARD_SKILL'

class Cli055ProfesionEstudio(models.Model):
    nombre = models.CharField(max_length=200)
    estado_id_001 = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)

    class Meta:
        #managed = False
        db_table = 'cli_055_profesion_estudio'

        verbose_name = 'PROFESION_ESTUDIO'
        verbose_name_plural = 'PROFESIONES_ESTUDIOS'
class Cli052Vacante(models.Model):
    ESTADO_VACANTE = [
        (1, 'Abierta'),
        (2, 'Cerrada'),
        (3, 'Cancelada'),
    ]

    EXPERIENCIA_TIEMPO = [
        (1, '0 a 6 Meses'),
        (2, '1 año a 2 años'),
        (3, 'Más de 2 años'),
        (4, 'Sin Experiencia'),
    ]

    titulo = models.CharField(max_length=200)
    numero_posiciones = models.IntegerField()
    profesion_estudio_id_055 = models.ForeignKey(Cli055ProfesionEstudio, on_delete=models.CASCADE)
    experiencia_requerida = models.IntegerField(choices=EXPERIENCIA_TIEMPO)
    soft_skills_id_053 = models.ManyToManyField(Cli053SoftSkill)
    hard_skills_id_054 = models.ManyToManyField(Cli054HardSkill)
    funciones_responsabilidades = models.TextField()
    ciudad = models.ForeignKey(Cat004Ciudad, on_delete=models.CASCADE)
    salario = models.IntegerField(null=True, blank=True)  # Opcional
    estado_vacante = models.IntegerField(choices=ESTADO_VACANTE, default=1)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, default=1)
    cliente_id_051 = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
    class Meta:
        #managed = False
        db_table = 'cli_052_vacante'

        verbose_name = 'VACANTE'
        verbose_name_plural = 'VACANTES'


class Cli052VacanteHardSkillsId054(models.Model):
    id = models.BigAutoField(primary_key=True)
    cli052vacante = models.ForeignKey(Cli052Vacante, models.DO_NOTHING)
    cli054hardskill = models.ForeignKey('Cli054HardSkill', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_052_vacante_hard_skills_id_054'
        unique_together = (('cli052vacante', 'cli054hardskill'),)


class Cli052VacanteSoftSkillsId053(models.Model):
    id = models.BigAutoField(primary_key=True)
    cli052vacante = models.ForeignKey(Cli052Vacante, models.DO_NOTHING)
    cli053softskill = models.ForeignKey('Cli053SoftSkill', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_052_vacante_soft_skills_id_053'
        unique_together = (('cli052vacante', 'cli053softskill'),)

class Cli056AplicacionVacante(models.Model):
    ESTADO_APLICACION = [
        (1, 'En proceso'),
        (2, 'Exitoso'),
        (3, 'Cancelado'),
        (4, 'Terminado'),
        (5, 'Desiste'),
    ]

    candidato_101 = models.ForeignKey(Can101Candidato, on_delete=models.CASCADE, related_name='aplicaciones')
    vacante_id_052 = models.ForeignKey(Cli052Vacante, on_delete=models.CASCADE, related_name='aplicaciones')
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado_aplicacion = models.IntegerField(choices=ESTADO_APLICACION, default=1)

    def __str__(self):
        return f"{self.candidato} - {self.vacante} - {self.get_estado_aplicacion_display()}"

    class Meta:
        db_table = 'cli_056_aplicacion_vacante'
        verbose_name = 'APLICACIÓN A VACANTE'
        verbose_name_plural = 'APLICACIONES A VACANTES'
        unique_together = ('candidato_101', 'vacante_id_052')  # Evita aplicaciones duplicadas