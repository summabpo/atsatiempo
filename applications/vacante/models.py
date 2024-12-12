from django.db import models
from django.db.models import Count
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.cliente.models import Cli051Cliente
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
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titulo
    
    @classmethod
    def contar_vacantes_por_estado(cls, cliente_id):
        total_vacantes = cls.objects.filter(cliente_id_051=cliente_id).count()
        
        activas = cls.objects.filter(estado_vacante=1, cliente_id_051=cliente_id).count()
        en_proceso = cls.objects.filter(estado_vacante=2, cliente_id_051=cliente_id).count()
        finalizadas = cls.objects.filter(estado_vacante=3, cliente_id_051=cliente_id).count()
        canceladas = cls.objects.filter(estado_vacante=4, cliente_id_051=cliente_id).count()
        
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

class Cli056AplicacionVacante(models.Model):
    ESTADO_APLICACION = [
        (1, 'Aplicado'),
        (2, 'Entrevista Programada'),
        (3, 'Entrevista Aprobada'),
        (4, 'Entrevista No Aprobada'),
        (5, 'Prueba Programada'),
        (6, 'Prueba Superada'),
        (7, 'Prueba No Superada'),
        (8, 'Seleccionado'),
        (9, 'Finalizada'),
        (10, 'Cancelada'),
        (11, 'Desiste'),
        (12, 'No Apto'),
    ]

    candidato_101 = models.ForeignKey(Can101Candidato, on_delete=models.CASCADE, related_name='aplicaciones')
    vacante_id_052 = models.ForeignKey(Cli052Vacante, on_delete=models.CASCADE, related_name='aplicaciones')
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado_aplicacion = models.IntegerField(choices=ESTADO_APLICACION, default=1)

    def __str__(self):
        return str(self.id)

    def calcular_cantidades_y_porcentajes(vacante_id):
        total_aplicaciones = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id).count()

        if total_aplicaciones == 0:
            return {
                'aplicadas': {'cantidad': 0, 'porcentaje': 0},
                'en_proceso': {'cantidad': 0, 'porcentaje': 0},
                'finalizadas': {'cantidad': 0, 'porcentaje': 0},
                'canceladas': {'cantidad': 0, 'porcentaje': 0},
                'desistidos': {'cantidad': 0, 'porcentaje': 0},
                'no_aptas': {'cantidad': 0, 'porcentaje': 0},
                'seleccionados': {'cantidad': 0, 'porcentaje': 0},
            }

        # Contar estados específicos
        aplicadas = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id, estado_aplicacion=1).count()
        en_proceso = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id, estado_aplicacion__in=[2, 3, 5, 6]).count()
        seleccionados = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id, estado_aplicacion=8).count()
        finalizadas = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id, estado_aplicacion=9).count()
        canceladas = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id, estado_aplicacion=10).count()
        desistidos = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id, estado_aplicacion=11).count()
        no_aptas = Cli056AplicacionVacante.objects.filter(vacante_id_052=vacante_id, estado_aplicacion=12).count()

        # Calcular porcentajes
        porcentaje_aplicadas = round((aplicadas / total_aplicaciones * 100), 1) if total_aplicaciones > 0 else 0
        porcentaje_en_proceso = round((en_proceso / total_aplicaciones * 100), 1) if total_aplicaciones > 0 else 0
        porcentaje_finalizadas = round((finalizadas / total_aplicaciones * 100), 1) if total_aplicaciones > 0 else 0
        porcentaje_canceladas = round((canceladas / total_aplicaciones * 100), 1) if total_aplicaciones > 0 else 0
        porcentaje_desistidos = round((desistidos / total_aplicaciones * 100), 1) if total_aplicaciones > 0 else 0
        porcentaje_no_aptas = round((no_aptas / total_aplicaciones * 100), 1) if total_aplicaciones > 0 else 0
        porcentaje_seleccionados = round((seleccionados / total_aplicaciones * 100), 1) if total_aplicaciones > 0 else 0

        return {
            'aplicadas': {'cantidad': aplicadas, 'porcentaje': porcentaje_aplicadas},
            'en_proceso': {'cantidad': en_proceso, 'porcentaje': porcentaje_en_proceso},
            'finalizadas': {'cantidad': finalizadas, 'porcentaje': porcentaje_finalizadas},
            'canceladas': {'cantidad': canceladas, 'porcentaje': porcentaje_canceladas},
            'desistidos': {'cantidad': desistidos, 'porcentaje': porcentaje_desistidos},
            'no_aptas': {'cantidad': no_aptas, 'porcentaje': porcentaje_no_aptas},
            'seleccionados': {'cantidad': seleccionados, 'porcentaje': porcentaje_seleccionados},
            'total_aplicaciones': total_aplicaciones,
        }
    class Meta:
        db_table = 'cli_056_aplicacion_vacante'
        verbose_name = 'APLICACIÓN A VACANTE'
        verbose_name_plural = 'APLICACIONES A VACANTES'
        unique_together = ('candidato_101', 'vacante_id_052')  # Evita aplicaciones duplicadas


class Cli057AsignacionEntrevista(models.Model):
    id = models.BigAutoField(primary_key=True)
    
    TIPO_ENTREVISTA = [
        ('V', 'Virtual'),
        ('P', 'Presencial'),
    ]
    
    ESTADO_ASIGNACION = [
        (1, 'Pendiente'),
        (2, 'Apto'),
        (3, 'No Apto'),
        (4, 'Seleccionado'),
        (5, 'Cancelado'),
    ]

    asignacion_vacante = models.ForeignKey(Cli056AplicacionVacante, on_delete=models.CASCADE, related_name='asignaciones_entrevista')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    usuario_asigno = models.ForeignKey(UsuarioBase, on_delete=models.SET_NULL, null=True, related_name='entrevistas_asignadas')
    usuario_asignado = models.ForeignKey(UsuarioBase, on_delete=models.SET_NULL, null=True, related_name='entrevistas_por_realizar')
    fecha_entrevista = models.DateField()
    hora_entrevista = models.TimeField()
    tipo_entrevista = models.CharField(max_length=1, choices=TIPO_ENTREVISTA)
    lugar_enlace = models.CharField(max_length=255)
    estado_asignacion = models.IntegerField(choices=ESTADO_ASIGNACION, default=1)
    estado = models.ForeignKey(Cat001Estado, models.DO_NOTHING, default=1)

    # campos post asignacion
    observacion = models.TextField(null=True, blank=True, verbose_name="Observación")
    fecha_gestion = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.id)
    
    def obtener_tipo_entrevista(self):
        return "Presencial" if self.tipo_entrevista == 'P' else "Virtual"

    #Método para obtener color
    def obtener_color(self):
        # Asignar un color según el estado
        if self.estado_asignacion == 1:
            return '#f39c12'  # Color naranja
        elif self.estado_asignacion == 2 or self.estado == 3 or self.estado == 4:
            return '#28a745'  # Color verde
        elif self.estado_asignacion == 5:
            return '#dc3545'  # Color rojo
        return '#007bff'  # Color por defecto (azul)
    
    def mostrar_estado_asignacion(self):
        if self.estado_asignacion == 1:
            return 'Pendiente'
        elif self.estado_asignacion == 2:
            return 'Apto'
        elif self.estado_asignacion == 3:
            return 'No Apto'
        elif self.estado_asignacion == 4:
            return 'Seleccionado'
        elif self.estado_asignacion == 5:
            return 'Cancelado'

    
    class Meta:
        db_table = 'cli_057_asignacion_entrevista'
        verbose_name = 'ASIGNACIÓN DE ENTREVISTA'
        verbose_name_plural = 'ASIGNACIONES DE ENTREVISTAS'
        # unique_together = ('asignacion_vacante', 'usuario_asignado', 'fecha_entrevista', 'hora_entrevista')  # Evita asignaciones duplicadas

    
class Cli063AplicacionVacanteHistorial(models.Model):
    aplicacion_vacante_056 = models.ForeignKey(
        Cli056AplicacionVacante, 
        on_delete=models.CASCADE, 
        related_name='historial'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    usuario_id_genero = models.ForeignKey(
        UsuarioBase,  # Cambia esto si usas otro modelo de usuario
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    )
    estado = models.IntegerField(choices=Cli056AplicacionVacante.ESTADO_APLICACION)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Historial {self.id} - Aplicación {self.aplicacion_vacante_056.id}"

    class Meta:
        db_table = 'cli_063_aplicacion_vacante_historial'
        verbose_name = 'Historial de Aplicación a Vacante'
        verbose_name_plural = 'Historiales de Aplicaciones a Vacantes'