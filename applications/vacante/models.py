from django.db import models
from django.db.models import Count
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.cliente.models import Cli051Cliente, Cli064AsignacionCliente, Cli068Cargo
from applications.candidato.models import Can101Candidato
from applications.usuarios.models import UsuarioBase

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
    estado_id_001 = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.id)
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
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    MODALIDAD_CHOICES = [
        ('R', 'Remoto'),
        ('P', 'Presencial'),
        ('H', 'Hibrido'),
    ]

    JORNADA_CHOICES = [
        ('T', 'Diurna'),   
        ('P', 'Nocturna'),
        ('R', 'Rotativa'),

    ]

    TIPO_SALARIO_CHOICES = [
        ('F', 'Fijo'),
        ('M', 'Mixto'),
        ('I', 'Integral'),
        ('H', 'Por Hora'),
        ('C', 'Convenio'),
    ]

    TERMINO_CONTRATO_CHOICES = [
        ('F', 'Fijo'),
        ('I', 'Indefinido'),
        ('O', 'Obra Labor'),
    ]

    EDAD_CHOICES = [
        ('1', '19-24 años'),
        ('2', '25-29 años'),
        ('3', '30-34 años'),
        ('4', '35-39 años'),
        ('5', '40-44 años'),
        ('6', '45-50 años'),
    ]

    TIEMPO_EXPERIENCIA_CHOICES = [
        (1, 'Sin experiencia'),
        (2, '1 año'),
        (3, '2 años'),
        (4, '3 años'),
        (5, '4 años'),
        (6, '5 años o más'),
    ]

    FRECUENCIA_PAGO_CHOICES = [
        ('S', 'Semanal'),
        ('Q', 'Quincenal'),
        ('M', 'Mensual'),
    ]

    NIVEL_ESTUDIO_CHOICES = [
        (1, 'Sin estudios'),
        (2, 'Primaria'),
        (3, 'Secundaria/Bachillerato'),
        (4, 'Técnico'),
        (5, 'Tecnólogo'),
        (6, 'Universitario'),
        (7, 'Postgrado'),
    ]

    edad = models.CharField(max_length=1, choices=EDAD_CHOICES)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    tiempo_experiencia = models.IntegerField(choices=TIEMPO_EXPERIENCIA_CHOICES, help_text="Tiempo de experiencia en años")
    horario = models.CharField(max_length=100)
    modalidad = models.CharField(max_length=1, choices=MODALIDAD_CHOICES)
    jornada = models.CharField(max_length=1, choices=JORNADA_CHOICES)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_salario = models.CharField(max_length=1, choices=TIPO_SALARIO_CHOICES)
    frecuencia_pago = models.CharField(max_length=1, choices=FRECUENCIA_PAGO_CHOICES)
    salario_adicional = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    idioma = models.CharField(max_length=100)
    profesion_estudio = models.ForeignKey(Cli055ProfesionEstudio, on_delete=models.CASCADE)
    nivel_estudio = models.IntegerField(choices=NIVEL_ESTUDIO_CHOICES)
    lugar_trabajo = models.ForeignKey(Cat004Ciudad, on_delete=models.CASCADE)
    termino_contrato = models.CharField(max_length=1, choices=TERMINO_CONTRATO_CHOICES)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, default=1)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Perfil Vacante {self.id} - {self.profesion_estudio}"

    class Meta:
        db_table = 'cli_072_perfil_vacante'
        verbose_name = 'PERFIL_VACANTE'
        verbose_name_plural = 'PERFILES_VACANTES'

class Cli052Vacante(models.Model):
    ESTADO_VACANTE = [
        (1, 'Activa'),
        (2, 'En Proceso'),
        (3, 'Finalizada'),
        (4, 'Cancelada'),
    ]

    EXPERIENCIA_TIEMPO = [
        (1, '0 a 6 Meses'),
        (2, '1 año a 2 años'),
        (3, '2 años de 3 años'),
        (4, 'Sin Experiencia'),
        (5, '3 años de 4 años'),
        (6, '4 años de 5 años'),
        (7, '5 años de 6 años'),
        (8, '6 años de 7 años'),
        (9, '7 años de 8 años'),
        (10, '8 años de 9 años'),
        (11, '9 años de 10 años'),
        (12, '10 años o más'),
    ]

    titulo = models.CharField(max_length=200)
    numero_posiciones = models.IntegerField()
    # profesion_estudio_id_055 = models.ForeignKey(Cli055ProfesionEstudio, on_delete=models.CASCADE)
    # experiencia_requerida = models.IntegerField(choices=EXPERIENCIA_TIEMPO)
    soft_skills_id_053 = models.ManyToManyField(Cli053SoftSkill)
    hard_skills_id_054 = models.ManyToManyField(Cli054HardSkill)
    # ciudad = models.ForeignKey(Cat004Ciudad, on_delete=models.CASCADE)
    # salario = models.IntegerField(null=True, blank=True)  # Opcional
    estado_vacante = models.IntegerField(choices=ESTADO_VACANTE, default=1)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, default=1)
    # cliente_id_051 = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    usuario_asignado = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, null=True, blank=True)
    asignacion_cliente_id_064 = models.ForeignKey(Cli064AsignacionCliente, on_delete=models.CASCADE, null=True, blank=True)
    cargo = models.ForeignKey(Cli068Cargo, on_delete=models.CASCADE, null=True, blank=True)

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