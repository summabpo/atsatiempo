from django.db import models
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.services.choices import GENERO_CHOICES_STATIC, MODALIDAD_CHOICES_STATIC, MOTIVO_SALIDA_CHOICES_STATIC, NIVEL_ESTUDIO_CHOICES_STATIC, NIVEL_HABILIDAD_CHOICES_STATIC, TIPO_HABILIDAD_CHOICES_STATIC
# Create your models here.
class Can101Candidato(models.Model):

    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    email = models.EmailField(unique=True)
    primer_nombre = models.CharField(max_length=50, verbose_name="Primer Nombre", blank=True, null=False)
    segundo_nombre = models.CharField(max_length=50, verbose_name="Segunndo Nombre", blank=True, null=True)
    primer_apellido = models.CharField(max_length=50, verbose_name="Primer Apellido", blank=True, null=False)
    segundo_apellido = models.CharField(max_length=50, verbose_name="Segundo Apellido", blank=True, null=True)
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004', blank=True, null=True)
    sexo = models.CharField(max_length=1, blank=True, null=True, choices=GENERO_CHOICES_STATIC)
    fecha_nacimiento = models.DateField(null=True, blank=True) 
    telefono = models.CharField(max_length=10, blank=True, null=True)
    skills = models.ManyToManyField('Can104Skill', through='Can101CandidatoSkill', related_name='candidatos_skill')
    imagen_perfil = models.ImageField(upload_to='media_uploads/media_uploads/candidato/', blank=True, null=True, verbose_name="Imagen de Perfil")
    hoja_de_vida = models.FileField(upload_to='media_uploads/media_uploads/hoja_de_vida/', blank=True, null=True, verbose_name="Hoja de Vida")
    video_perfil = models.FileField(upload_to='media_uploads/media_uploads/videos_candidato/', blank=True, null=True, verbose_name="Video de Perfil", help_text="Sube un video desde tu dispositivo móvil o web")
    numero_documento = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    perfil = models.TextField(blank=True, null=True, verbose_name="Perfil del Candidato")
    aspiracion_salarial = models.IntegerField(blank=True, null=True, verbose_name="Aspiración Salarial")
    fit_cultural = models.JSONField(blank=True, null=True, verbose_name="Fit Cultural", help_text="Fit cultural en formato JSON")
    motivadores = models.JSONField(blank=True, null=True, verbose_name="Motivadores", help_text="Motivadores en formato JSON")
    
    
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
    fecha_final = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=False)
    logro = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)
    cargo = models.CharField(max_length=100)
    motivo_salida = models.IntegerField(choices=MOTIVO_SALIDA_CHOICES_STATIC, blank=True, null=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    modalidad_trabajo = models.CharField(max_length=1, blank=True, null=True, choices=MODALIDAD_CHOICES_STATIC)
    nombre_jefe = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.entidad
    class Meta:
        managed = True
        db_table = 'can_102_experiencia'

        verbose_name = 'EXPERIENCIA'
        verbose_name_plural = 'EXPERIENCIAS'

class Can103Educacion(models.Model):
    
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    institucion = models.CharField(max_length=100, blank=False, null=False)
    fecha_inicial = models.DateField(blank=False, null=False)
    fecha_final = models.DateField(blank=False, null=True)
    grado_en = models.BooleanField(default=False)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    carrera = models.CharField(max_length=100, blank=True, null=True)
    fortaleza_adquiridas = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004', blank=True, null=True)
    tipo_estudio = models.CharField(max_length=2, choices=NIVEL_ESTUDIO_CHOICES_STATIC, blank=True, null=True)
    certificacion = models.FileField(upload_to='media_uploads/media_uploads/certificaciones/', blank=True, null=True, verbose_name="Certificación")
    profesion_estudio = models.ForeignKey('vacante.Cli055ProfesionEstudio', on_delete=models.CASCADE, db_column='profesion_estudio_id_055', blank=True, null=True, verbose_name="Profesión/Estudio")

    def mostrar_tipo_estudio(self):
        return dict(NIVEL_ESTUDIO_CHOICES_STATIC).get(self.tipo_estudio, "No especificado")

    def __str__(self):
        return self.institucion
    class Meta:
        #managed = False
        db_table = 'can_103_educacion'

        verbose_name = 'EDUCACION'

class Can107GrupoSkill(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Grupo de Skill")
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'can_107_grupo_skill'
        verbose_name = 'GRUPO SKILL'
        verbose_name_plural = 'GRUPOS SKILL'

class Can104Skill(models.Model):
    estado_id_004 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_004')
    nombre = models.CharField(max_length=50)
    grupo = models.ForeignKey(Can107GrupoSkill, on_delete=models.CASCADE, db_column='grupo_id_107', blank=True, null=True, verbose_name="Grupo de Skill")

    def __str__(self):
        return self.nombre
    class Meta:
        #managed = False
        db_table = 'can_104_skill'
        verbose_name = 'SKILL'

class Can101CandidatoSkill(models.Model):
    candidato_id_101 = models.ForeignKey(Can101Candidato, on_delete=models.CASCADE, db_column='candidato_id_101')
    skill_id_104 = models.ForeignKey(Can104Skill, on_delete=models.CASCADE, db_column='skill_id_104')
    nivel= models.IntegerField(choices=NIVEL_HABILIDAD_CHOICES_STATIC)
    tipo_habilidad = models.CharField(max_length=1, choices=TIPO_HABILIDAD_CHOICES_STATIC, verbose_name="Tipo de Habilidad", blank=True, null=True)
    certificado_habilidad = models.FileField(upload_to='media_uploads/media_uploads/certificados_habilidad/', blank=True, null=True, verbose_name="Certificado de Habilidad")

    def color_nivel(self):
        colores = {
            1: 'info',      # Básico
            2: 'warning',   # Intermedio
            3: 'success',   # Superior
        }
        return colores.get(self.nivel, 'secondary')

    class Meta:
        # managed = False 
        db_table = 'can_101_candidato_skills'       

class Can105RedSocial(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre", blank=True, null=True)
    logo = models.ImageField(upload_to='media_uploads/media_uploads/logos_redes/', blank=True, null=True, verbose_name="Logo de la Red Social")
    url_principal = models.URLField(max_length=200, verbose_name="URL Principal de la Red Social", blank=True, null=True)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        #managed = False
        db_table = 'can_105_red_social'
        verbose_name = 'RED SOCIAL'
        verbose_name_plural = 'REDES SOCIALES'

class Can106CandidatoRed(models.Model):
    candidato_id_101 = models.ForeignKey(Can101Candidato, on_delete=models.CASCADE, db_column='candidato_id_101')
    red_social_id_105 = models.ForeignKey(Can105RedSocial, on_delete=models.CASCADE, db_column='red_social_id_105')
    url = models.URLField(max_length=255, verbose_name="URL del Perfil", blank=True, null=True)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')

    def __str__(self):
        return f"{self.candidato_id_101} - {self.red_social_id_105}"

    class Meta:
        db_table = 'can_106_candidato_red'
        verbose_name = 'CANDIDATO RED'
        verbose_name_plural = 'CANDIDATOS REDES'