from django.db import models
from django.db.models import Count
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente, Cli068Cargo, Cli077FitCultural, Cli078MotivadoresCandidato
from applications.candidato.models import Can101Candidato, Can104Skill
from applications.usuarios.models import UsuarioBase

#choices
from applications.services.choices import EDAD_CHOICES_STATIC, GENERO_CHOICES_STATIC, HORARIO_CHOICES_STATIC, IDIOMA_CHOICES_STATIC, NIVEL_IDIOMA_CHOICES_STATIC, TIEMPO_EXPERIENCIA_CHOICES_STATIC, MODALIDAD_CHOICES_STATIC, JORNADA_CHOICES_STATIC, TIPO_PROFESION_CHOICES_STATIC, TIPO_SALARIO_CHOICES_STATIC, FRECUENCIA_PAGO_CHOICES_STATIC, NIVEL_ESTUDIO_CHOICES_STATIC, TERMINO_CONTRATO_CHOICES_STATIC , ESTADO_VACANTE_CHOICHES_STATIC, TIPO_HORARIO_CHOICES_STATIC

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

class Cli075GrupoProfesion(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre", blank=False, null=False)
    estado = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')

    def __str__(self):
        return self.nombre

    @property
    def profesiones(self):
        """Retorna todas las profesiones que pertenecen a este grupo"""
        return self.cli055profesionestudio_set.filter(estado_id_001=1).order_by('nombre')

    class Meta:
        db_table = 'cli_075_grupo_profesion'
        verbose_name = 'GRUPO PROFESIÓN'
        verbose_name_plural = 'GRUPOS PROFESIÓN'

class Cli055ProfesionEstudio(models.Model):
    nombre = models.CharField(max_length=200)
    estado_id_001 = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, default=1)
    grupo = models.ForeignKey(Cli075GrupoProfesion, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nombre
    class Meta:
        #managed = False
        db_table = 'cli_055_profesion_estudio'

        verbose_name = 'PROFESION_ESTUDIO'
        verbose_name_plural = 'PROFESIONES_ESTUDIOS'

class Cli072FuncionesResponsabilidades(models.Model):
    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'cli_072_funciones_responsabilidades'
        verbose_name = 'FUNCION_RESPONSABILIDAD'
        verbose_name_plural = 'FUNCIONES_RESPONSABILIDADES'

class Cli073PerfilVacante(models.Model):

    edad_inicial = models.IntegerField(blank=True, null=True)
    edad_final = models.IntegerField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES_STATIC)
    tiempo_experiencia = models.IntegerField(choices=TIEMPO_EXPERIENCIA_CHOICES_STATIC, help_text="Tiempo de experiencia en años")
    modalidad = models.CharField(max_length=1, choices=MODALIDAD_CHOICES_STATIC)
    jornada = models.CharField(max_length=1, choices=JORNADA_CHOICES_STATIC)
    salario = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    tipo_salario = models.CharField(max_length=1, choices=TIPO_SALARIO_CHOICES_STATIC)
    frecuencia_pago = models.CharField(max_length=1, choices=FRECUENCIA_PAGO_CHOICES_STATIC)
    salario_adicional = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    idioma = models.CharField(max_length=100, choices=IDIOMA_CHOICES_STATIC, blank=True, null=True)
    nivel_idioma = models.CharField(max_length=2, choices=NIVEL_IDIOMA_CHOICES_STATIC, blank=True, null=True)
    tipo_profesion = models.CharField(max_length=1, choices=TIPO_PROFESION_CHOICES_STATIC, blank=True, null=True)
    profesion_estudio = models.ForeignKey(Cli055ProfesionEstudio, on_delete=models.CASCADE, blank=True, null=True)
    grupo_profesion = models.ForeignKey(Cli075GrupoProfesion, on_delete=models.CASCADE, blank=True, null=True)
    profesion_estudio_listado = models.TextField(blank=True, null=True)
    nivel_estudio = models.CharField(max_length=1, choices=NIVEL_ESTUDIO_CHOICES_STATIC, blank=True, null=True)
    cantidad_semestres = models.IntegerField(blank=True, null=True)
    estado_estudio = models.BooleanField(default=False, blank=True, null=True)
    lugar_trabajo = models.ForeignKey(Cat004Ciudad, on_delete=models.CASCADE)
    barrio  = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    url_mapa = models.URLField(max_length=1000, blank=True, null=True)
    termino_contrato = models.CharField(max_length=1, choices=TERMINO_CONTRATO_CHOICES_STATIC)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, default=1)
    fecha_creacion = models.DateField(auto_now_add=True)
    tipo_horario = models.CharField(max_length=2, choices=TIPO_HORARIO_CHOICES_STATIC, blank=True, null=True, help_text="Tipo de horario: Fijo, Rotativo o Flexible")
    horario_inicio = models.CharField(max_length=1, choices=HORARIO_CHOICES_STATIC, blank=True, null=True)
    horario_final = models.CharField(max_length=1, choices=HORARIO_CHOICES_STATIC, blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_final = models.TimeField(blank=True, null=True)
    motivo_vacante = models.JSONField(blank=True, null=True, help_text="Motivo de la vacante en formato JSON")
    horario = models.JSONField(blank=True, null=True, help_text="Horario de trabajo en formato JSON")

    experiencia_laboral = models.JSONField(blank=True, null=True, help_text="Experiencia laboral en formato JSON")
    idiomas = models.JSONField(blank=True, null=True, help_text="Idiomas en formato JSON")
    estudio_complementario = models.JSONField(blank=True, null=True, help_text="Estudios complementarios en formato JSON")
    funciones_responsabilidades = models.JSONField(blank=True, null=True, help_text="Funciones en formato JSON")
    

    def __str__(self):
        return f"Perfil Vacante {self.id} - {self.profesion_estudio}"

    class Meta:
        db_table = 'cli_072_perfil_vacante'
        verbose_name = 'PERFIL_VACANTE'
        verbose_name_plural = 'PERFILES_VACANTES'

class Cli052Vacante(models.Model):
    
    titulo = models.CharField(max_length=200)
    numero_posiciones = models.IntegerField()
    cantidad_presentar = models.IntegerField(blank=True, null=True)
    soft_skills_id_053 = models.ManyToManyField(Cli053SoftSkill)
    hard_skills_id_054 = models.ManyToManyField(Cli054HardSkill)
    fit_cultural = models.ManyToManyField(Cli077FitCultural)
    # motivadores = models.ManyToManyField(Cli078MotivadoresCandidato, on_delete=models.CASCADE, blank=True, null=True)
    motivadores = models.ManyToManyField(Cli078MotivadoresCandidato, related_name="motivadores_vacante")
    otro_motivador = models.CharField(max_length=100, blank=True, null=True)
    estudios_complementarios = models.CharField(max_length=100, blank=True, null=True)
    estudios_complementarios_certificado = models.BooleanField(default=False, blank=True, null=True)
    estado_vacante = models.IntegerField(choices=ESTADO_VACANTE_CHOICHES_STATIC, default=1)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_presentacion = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    usuario_asignado = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, null=True, blank=True, related_name='vacantes_usuario_asignado')
    asignacion_cliente_id_064 = models.ForeignKey(Cli064AsignacionCliente, on_delete=models.CASCADE, null=True, blank=True)
    cargo = models.ForeignKey(Cli068Cargo, on_delete=models.CASCADE, null=True, blank=True)
    perfil_vacante = models.ForeignKey(Cli073PerfilVacante, on_delete=models.CASCADE, null=True, blank=True)
    descripcion_vacante = models.TextField(null=True, blank=True)
    comentarios = models.TextField(null=True, blank=True)
    habilidades = models.ManyToManyField(Can104Skill, related_name="habilidades_vacante")
    motivadores_multiple = models.ManyToManyField(Cli078MotivadoresCandidato, related_name="motivadores_multiple_vacante")
    data_asignacion_usuario = models.JSONField(null=True, blank=True)
    asignacion_reclutador = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, null=True, blank=True, related_name='vacantes_asignacion_reclutador')
    data_asignacion_reclutador = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.titulo

    @classmethod
    def contar_vacantes_por_estado(cls, cliente_id):
        total_vacantes = cls.objects.filter(cliente_id_051=cliente_id).count()
        
        activas = cls.objects.filter(estado_vacante=1, estado_id_001=1, cliente_id_051=cliente_id).count()
        en_proceso = cls.objects.filter(estado_vacante=2, estado_id_001=1, cliente_id_051=cliente_id).count()
        finalizadas = cls.objects.filter(estado_vacante=3, estado_id_001=1, cliente_id_051=cliente_id).count()
        canceladas = cls.objects.filter(estado_vacante=4, estado_id_001=1, cliente_id_051=cliente_id).count()
        
        # Evitar división por cero
        porcentaje_activas = round((activas / total_vacantes * 100), 1) if total_vacantes > 0 else 0
        porcentaje_en_proceso = round((en_proceso / total_vacantes * 100), 1) if total_vacantes > 0 else 0
        porcentaje_finalizadas = round((finalizadas / total_vacantes * 100), 1) if total_vacantes > 0 else 0
        porcentaje_canceladas = round((canceladas / total_vacantes * 100), 1) if total_vacantes > 0 else 0

        
        return {
            'activas': {'cantidad': activas, 'porcentaje': porcentaje_activas},
            'en_proceso': {'cantidad': en_proceso, 'porcentaje': porcentaje_en_proceso},
            'finalizadas': {'cantidad': finalizadas, 'porcentaje': porcentaje_finalizadas},
            'canceladas': {'cantidad': canceladas, 'porcentaje': porcentaje_canceladas},
            'total_vacantes': total_vacantes,
        }

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

class Cli074AsignacionFunciones(models.Model):
    vacante = models.ForeignKey(Cli052Vacante, on_delete=models.CASCADE)
    funcion_responsabilidad = models.ForeignKey(Cli072FuncionesResponsabilidades, on_delete=models.CASCADE)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vacante} - {self.funcion_responsabilidad}"

    class Meta:
        db_table = 'cli_074_asignacion_funciones'
        verbose_name = 'ASIGNACION_FUNCION'
        verbose_name_plural = 'ASIGNACIONES_FUNCIONES'
        unique_together = (('vacante', 'funcion_responsabilidad'),)