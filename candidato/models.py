from django.db import models
from common.models import Cat001Estado, Cat004Ciudad
# Create your models here.
class Can101Candidato(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    email = models.EmailField(unique=True)
    primer_nombre = models.TextField(max_length=50, verbose_name="Primer Nombre", blank=True, null=False)
    segundo_nombre = models.TextField(max_length=50, verbose_name="Segunndo Nombre", blank=True, null=True)
    primer_apellido = models.TextField(max_length=50, verbose_name="Primer Apellido", blank=True, null=False)
    segundo_apellido = models.TextField(max_length=50, verbose_name="Segundo Apellido", blank=True, null=True)
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004', blank=True, null=True)
    sexo = models.TextField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'can_101_candidato'

        verbose_name = 'CANDIDATO'
        verbose_name_plural = 'CANDIDATOS'

class Can102Experiencia(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    entidad = models.TextField()
    sector = models.TextField()
    fecha_inicial = models.DateTimeField()
    fecha_final = models.DateTimeField(blank=True, null=True)
    activo = models.IntegerField()
    logro = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'can_102_experiencia'

        verbose_name = 'EXPERIENCIA'
        verbose_name_plural = 'EXPERIENCIAS'


class Can103Educacion(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    institucion = models.TextField()
    fecha_inicial = models.DateTimeField()
    fecha_final = models.DateTimeField(blank=True, null=True)
    grado_en = models.TextField(blank=True, null=True)
    titulo = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'can_103_educacion'

        verbose_name = 'EDUCACION'


class Can104Skill(models.Model):
    estado_id_004 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_004')
    nombre = models.TextField()

    class Meta:
        #managed = False
        db_table = 'can_104_skill'

        verbose_name = 'SKILL'


class Can105SkillCandidato(models.Model):
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101')
    skill_id_104 = models.ForeignKey(Can104Skill, models.DO_NOTHING, db_column='skill_id_104')

    class Meta:
        #managed = False
        db_table = 'can_105_skill_candidato'
