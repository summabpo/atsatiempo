from django.db import models
from applications.common.models import Cat001Estado, Cat004Ciudad
# Create your models here.
class Can101Candidato(models.Model):

    SEXO_CHOICES = (
        ('1', 'FEMENINO'),
        ('2', 'MASCULINO'),
    )

    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    email = models.EmailField(unique=True)
    primer_nombre = models.CharField(max_length=50, verbose_name="Primer Nombre", blank=True, null=False)
    segundo_nombre = models.CharField(max_length=50, verbose_name="Segunndo Nombre", blank=True, null=True)
    primer_apellido = models.CharField(max_length=50, verbose_name="Primer Apellido", blank=True, null=False)
    segundo_apellido = models.CharField(max_length=50, verbose_name="Segundo Apellido", blank=True, null=True)
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004', blank=True, null=True)
    sexo = models.CharField(max_length=1, blank=True, null=True, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField(null=True, blank=True) 
    telefono = models.CharField(max_length=10, blank=True, null=True)
    skills = models.ManyToManyField('Can104Skill', through='Can101CandidatoSkill', related_name='candidatos_skill')
    imagen_perfil = models.ImageField(upload_to='candidato/', blank=True, null=True, verbose_name="Imagen de Perfil")
    hoja_de_vida = models.FileField(upload_to='hoja_de_vida/', blank=True, null=True, verbose_name="Hoja de Vida")
    numero_documento = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.email
    class Meta:
        #managed = False
        db_table = 'can_101_candidato'

        verbose_name = 'CANDIDATO'
        verbose_name_plural = 'CANDIDATOS'
    
    def calcular_porcentaje(self):
        # Porcentajes individuales
        porcentaje_academico = 35
        porcentaje_laboral = 35
        porcentaje_habilidades = 30

        # Variables de cálculo
        tiene_academico = Can103Educacion.objects.filter(candidato_id_101=self.pk).exists()
        tiene_laboral = Can102Experiencia.objects.filter(candidato_id_101=self.pk).exists()
        tiene_habilidades = Can101CandidatoSkill.objects.filter(candidato_id_101=self.pk).exists()

        # Calcular porcentaje acumulado
        porcentaje = 0
        if tiene_academico:
            porcentaje += porcentaje_academico
        if tiene_laboral:
            porcentaje += porcentaje_laboral
        if tiene_habilidades:
            porcentaje += porcentaje_habilidades

        
        return porcentaje
    
    def puede_aplicar(self):
        # Definir el porcentaje mínimo para aplicar
        porcentaje_minimo = 80
        return self.calcular_porcentaje() >= porcentaje_minimo
    
    def nombre_completo(self):
        nombres = [self.primer_nombre, self.segundo_nombre, self.primer_apellido, self.segundo_apellido]
        return " ".join(filter(None, nombres))

class Can102Experiencia(models.Model):

    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    entidad = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    fecha_inicial = models.DateField(blank=True, null=True)
    fecha_final = models.DateField(blank=True, null=False)
    activo = models.BooleanField(default=False)
    logro = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)
    cargo = models.CharField(max_length=100)
    

    def __str__(self):
        return self.entidad
    class Meta:
        managed = True
        db_table = 'can_102_experiencia'

        verbose_name = 'EXPERIENCIA'
        verbose_name_plural = 'EXPERIENCIAS'

class Can103Educacion(models.Model):
    TIPO_ESTUDIO_CHOICES = (
        ('1', 'Primaria'),
        ('2', 'Bachillerato'),
        ('3', 'Técnico'),
        ('4', 'Tecnólogo'),
        ('5', 'Profesional'),
        ('6', 'Maestría'),
        ('7', 'Doctorado'),
    )
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    institucion = models.CharField(max_length=100, blank=False, null=False)
    fecha_inicial = models.DateField(blank=False, null=False)
    fecha_final = models.DateField(blank=False, null=True)
    grado_en = models.BooleanField(default=False)
    titulo = models.CharField(max_length=100, blank=False, null=False)
    carrera = models.CharField(max_length=100, blank=True, null=True)
    fortaleza_adquiridas = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004', blank=True, null=True)
    tipo_estudio = models.CharField(max_length=1, choices=TIPO_ESTUDIO_CHOICES, blank=True, null=True)
    def __str__(self):
        return self.institucion
    class Meta:
        #managed = False
        db_table = 'can_103_educacion'

        verbose_name = 'EDUCACION'

class Can104Skill(models.Model):
    estado_id_004 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_004')
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    class Meta:
        #managed = False
        db_table = 'can_104_skill'

        verbose_name = 'SKILL'

class Can101CandidatoSkill(models.Model):
    candidato_id_101 = models.ForeignKey(Can101Candidato, on_delete=models.CASCADE, db_column='candidato_id_101')
    skill_id_104 = models.ForeignKey(Can104Skill, on_delete=models.CASCADE, db_column='skill_id_104')
    nivel= models.IntegerField(choices=[
        (1, 'Básico'),
        (2, 'Intermedio'),
        (3, 'Superior')
    ])

    class Meta:
        # managed = False 
        db_table = 'can_101_candidato_skills'