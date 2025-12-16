from django.db import models
from django.db.models import Count
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.cliente.models import Cli051Cliente
from applications.candidato.models import Can101Candidato
from applications.services.choices import ESTADO_APLICACION_CHOICES_STATIC, ESTADO_APLICACION_COLOR_STATIC, ESTADO_RECLUTADO_CHOICES_STATIC
from applications.usuarios.models import UsuarioBase
from applications.vacante.models import Cli052Vacante

# Create your models here.
class Cli056AplicacionVacante(models.Model):

    candidato_101 = models.ForeignKey(Can101Candidato, on_delete=models.CASCADE, related_name='aplicaciones')
    vacante_id_052 = models.ForeignKey(Cli052Vacante, on_delete=models.CASCADE, related_name='aplicaciones')
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado_aplicacion = models.IntegerField(choices=ESTADO_APLICACION_CHOICES_STATIC, default=1)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.SET_NULL, null=True, blank=True, related_name='aplicaciones_vacante')
    preguntas_reclutamiento = models.JSONField(null=True, blank=True)
    json_match = models.JSONField(null=True, blank=True)
    estado_reclutamiento = models.IntegerField(choices=ESTADO_RECLUTADO_CHOICES_STATIC, default=1)

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
    
    def obtener_estado_con_color(self):
        estado_nombre, color = ESTADO_APLICACION_COLOR_STATIC.get(self.estado_aplicacion, ('Desconocido', 'gris'))
        return {'estado': estado_nombre, 'color': color}
    class Meta:
        db_table = 'cli_056_aplicacion_vacante'
        verbose_name = 'APLICACIÓN A VACANTE'
        verbose_name_plural = 'APLICACIONES A VACANTES'
        unique_together = ('candidato_101', 'vacante_id_052')  # Evita aplicaciones duplicadas

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
    estado = models.IntegerField(choices=ESTADO_APLICACION_CHOICES_STATIC)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Historial {self.id} - Aplicación {self.aplicacion_vacante_056.id}"

    class Meta:
        db_table = 'cli_063_aplicacion_vacante_historial'
        verbose_name = 'Historial de Aplicación a Vacante'
        verbose_name_plural = 'Historiales de Aplicaciones a Vacantes'