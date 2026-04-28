from datetime import timedelta
from django.db import models
from django.db.models import Count
from django.utils import timezone
from applications.common.models import Cat001Estado, Cat004Ciudad, Cat005AsignacionQr
from applications.cliente.models import Cli051Cliente, Cli069Requisito, Cli070AsignacionRequisito, Cli085AccionesDecisivas
from applications.candidato.models import Can101Candidato, Can102Experiencia
from applications.services.choices import ESTADO_APLICACION_CHOICES_STATIC, ESTADO_APLICACION_COLOR_STATIC, ESTADO_RECLUTADO_CHOICES_STATIC
from applications.usuarios.models import UsuarioBase
from applications.vacante.models import Cli052Vacante

def calcular_fecha_expiracion():
    """Función para calcular la fecha de expiración (2 días desde ahora)"""
    return timezone.now() + timedelta(days=2)

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
    usuario_reclutador = models.ForeignKey(UsuarioBase, on_delete=models.SET_NULL, null=True, blank=True, related_name='aplicaciones_reclutador')
    registro_reclutamiento = models.JSONField(null=True, blank=True)
    json_match_inicial = models.JSONField(null=True, blank=True)
    json_politicas_internas = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @classmethod
    def contar_estado_seleccionado(cls, vacante_id):
        """Cantidad de aplicaciones con estado_aplicacion = 8 (Seleccionado) para una vacante."""
        return cls.objects.filter(
            vacante_id_052=vacante_id, estado_aplicacion=8
        ).count()

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


class Cli079RequisitosCargado(models.Model):
    aplicacion_vacante_056 = models.ForeignKey(Cli056AplicacionVacante, on_delete=models.CASCADE, related_name='requisitos_cargados')
    asignacion_requisito_070 = models.ForeignKey(Cli070AsignacionRequisito, on_delete=models.CASCADE, related_name='requisitos_cargados')
    archivo_requisito = models.FileField(upload_to='media_uploads/requisitos/', blank=True, null=True, verbose_name="Archivo Requisito")
    fecha_cargado = models.DateTimeField(auto_now_add=True)
    usuario_cargado = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, related_name='requisitos_cargados')
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, related_name='requisitos_cargados')

    def __str__(self):
        return f"Requisito {self.asignacion_requisito_070.requisito.nombre} cargado para la aplicación {self.aplicacion_vacante_056.id}"

    class Meta:
        db_table = 'cli_079_requisitos_cargado'
        verbose_name = 'REQUISITO CARGADO'
        verbose_name_plural = 'REQUISITOS CARGADOS'
        unique_together = ('aplicacion_vacante_056', 'asignacion_requisito_070')

class Cli080DocumentoFirmadoAplicacionVacante(models.Model):
    aplicacion_vacante_056 = models.ForeignKey(Cli056AplicacionVacante, on_delete=models.CASCADE, related_name='documentos_firmar')
    imagen_firmada = models.ImageField(upload_to='media_uploads/firmas/', blank=True, null=True, verbose_name="Imagen Firma")
    ip_firmante = models.CharField(max_length=100, blank=True, null=True)
    fecha_firma_hora_ip = models.DateTimeField(auto_now_add=True)
    usuario_firmante = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, related_name='documentos_firmados')
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, related_name='documentos_firmados')
    documento_firmado = models.FileField(upload_to='media_uploads/documentos_firmados/', blank=True, null=True, verbose_name="Documento Firmado")
    codigo_unico = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Documento firmado para la aplicación {self.aplicacion_vacante_056.id}"

    class Meta:
        db_table = 'cli_080_documentos_firmar_aplicacion_vacante'
        verbose_name = 'DOCUMENTO FIRMAR APLICACIÓN A VACANTE'
        verbose_name_plural = 'DOCUMENTOS FIRMAR APLICACIONES A VACANTES'


class Cli081TokenGeneradoDocumentos(models.Model):
    aplicacion_vacante_056 = models.ForeignKey(Cli056AplicacionVacante, on_delete=models.CASCADE, related_name='aplicacion_vacante_token_generado')
    token = models.CharField(max_length=100, blank=True, null=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(default=calcular_fecha_expiracion)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, null=True, blank=True, related_name='token_generado_documentos')
    usuario_generador = models.ForeignKey(UsuarioBase, on_delete=models.SET_NULL, null=True, blank=True, related_name='token_generado_documentos')

    def __str__(self):
        return f"Token {self.token} generado para la aplicación {self.aplicacion_vacante_056.id}"
    class Meta:
        db_table = 'cli_081_token_generado_documentos'
        verbose_name = 'TOKEN GENERADO DOCUMENTOS'
        verbose_name_plural = 'TOKEN GENERADOS DOCUMENTOS'
        unique_together = ('aplicacion_vacante_056', 'token')
        

class Cli082PruebaCargada(models.Model):
    aplicacion_vacante_056 = models.ForeignKey(Cli056AplicacionVacante, on_delete=models.CASCADE, related_name='aplicacion_vacante_prueba_cargada')
    prueba_cargada = models.FileField(upload_to='media_uploads/pruebas/', blank=True, null=True, verbose_name="Prueba Cargada")
    fecha_cargada = models.DateTimeField(auto_now_add=True)
    usuario_cargada = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, related_name='prueba_cargada')
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, related_name='prueba_cargada')

    def __str__(self):
        return f"Prueba cargada para la aplicación {self.aplicacion_vacante_056.id}"

    class Meta:
        db_table = 'cli_082_prueba_cargada'
        verbose_name = 'PRUEBA CARGADA'
        verbose_name_plural = 'PRUEBAS CARGADAS'


class Cli083ConfiabilidadRiesgoCargado(models.Model):
    """Documento de índice y confiabilidad del riesgo asociado a la aplicación (entrevista)."""
    aplicacion_vacante_056 = models.ForeignKey(Cli056AplicacionVacante, on_delete=models.CASCADE, related_name='confiabilidad_riesgo_cargados')
    documento_cargado = models.FileField(upload_to='media_uploads/confiabilidad_riesgo/', blank=True, null=True, verbose_name="Documento Confiabilidad/Riesgo")
    fecha_cargado = models.DateTimeField(auto_now_add=True)
    usuario_cargado = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, related_name='confiabilidad_riesgo_cargados')
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, related_name='confiabilidad_riesgo_cargados')

    def __str__(self):
        return f"Confiabilidad/riesgo cargado para la aplicación {self.aplicacion_vacante_056.id}"

    class Meta:
        db_table = 'cli_083_confiabilidad_riesgo_cargado'
        verbose_name = 'CONFIABILIDAD RIESGO CARGADO'
        verbose_name_plural = 'CONFIABILIDAD RIESGO CARGADOS'


class Cli084AsignacionRegistroReclutado(models.Model):
    """Registro de candidatos que se registraron mediante el QR del reclutador."""
    estado = models.ForeignKey(Cat001Estado, on_delete=models.DO_NOTHING, db_column='estado_id_001', related_name='asignaciones_registro_reclutado')
    usuario_registrado = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE, db_column='usuario_registrado', related_name='registros_qr_reclutador')
    asignacion_qr_005 = models.ForeignKey(Cat005AsignacionQr, on_delete=models.CASCADE, db_column='asignacion_qr_005', related_name='registros_reclutados')
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registro {self.id} - {self.fecha_hora}"

    class Meta:
        db_table = 'cli_084_asignacion_registro_reclutado'
        verbose_name = 'ASIGNACIÓN REGISTRO RECLUTADO'
        verbose_name_plural = 'ASIGNACIONES REGISTRO RECLUTADO'


class Cli087ReporteAccionDecisivaReclutado(models.Model):
    """Modelo para reporte de acción decisiva reclutado."""
    aplicacion_vacante_056 = models.ForeignKey(
        Cli056AplicacionVacante, 
        on_delete=models.CASCADE, 
        related_name='reportes_accion_decisiva'
    )
    accion_decisiva = models.ForeignKey(
        Cli085AccionesDecisivas,
        on_delete=models.CASCADE,
        related_name='reportes_accion_decisiva'
    )
    archivo_reporte = models.FileField(
        upload_to='media_uploads/reporte_accion_decisiva/', 
        blank=True, 
        null=True, 
        verbose_name="Reporte Acción Decisiva"
    )
    fecha_cargado = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de cargado"
    )
    usuario_cargado = models.ForeignKey(
        UsuarioBase, 
        on_delete=models.CASCADE, 
        related_name='reportes_accion_decisiva_cargados'
    )
    estado = models.ForeignKey(
        Cat001Estado, 
        on_delete=models.CASCADE, 
        related_name='reportes_accion_decisiva'
    )
    json_data = models.JSONField(
        blank=True, 
        null=True, 
        verbose_name="Datos del reporte"
    )

    ACCION_DECISIVA_ESTADO_CHOICES = [
        ('aprobada', 'Aprobada'),
        ('pendiente', 'Pendiente'),
        ('no_aprobada', 'No aprobada'),
    ]
    estado_accion_decisiva = models.CharField(
        max_length=20,
        choices=ACCION_DECISIVA_ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado Acción Decisiva"
    )

    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario_actualizado = models.ForeignKey(
        UsuarioBase, 
        on_delete=models.CASCADE, 
        related_name='reportes_accion_decisiva_actualizados'
    )

    def __str__(self):
        return f"Reporte Acción Decisiva para la aplicación {self.aplicacion_vacante_056.id}"

    class Meta:
        db_table = 'cli_087_reporte_accion_decisiva_reclutado'
        verbose_name = 'REPORTE ACCIÓN DECISIVA RECLUTADO'
        verbose_name_plural = 'REPORTES ACCIÓN DECISIVA RECLUTADO'


class Cli088ReferenciasLaborales(models.Model):
    """
    Validación de referencias/experiencia laboral diligenciada por el cliente.

    Basado en el formulario "VALIDACIÓN DE DATOS (Cliente)".
    """

    reporte_accion_decisiva_087 = models.ForeignKey(
        Cli087ReporteAccionDecisivaReclutado,
        on_delete=models.CASCADE,
        related_name="referencias_laborales",
    )

    experiencia_candidato_102 = models.ForeignKey(
        Can102Experiencia,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="validaciones_referencias",
        help_text="Experiencia laboral del candidato (can_102_experiencia) referenciada por esta validación.",
    )

    # Verificación de empleo
    candidato_trabajo_en_empresa = models.BooleanField(null=True, blank=True)
    periodo_empleo_coincide = models.BooleanField(null=True, blank=True)

    # Verificación de cargo y jefe (texto + verificación sí/no)
    
    cargo_mencionado_verificado = models.BooleanField(null=True, blank=True)
    jefe_mencionado_verificado = models.BooleanField(null=True, blank=True)

    # Pregunta clave
    volveria_a_contratar = models.BooleanField(null=True, blank=True)

    # Revisión final y cierre
    validado_por = models.ForeignKey(
        UsuarioBase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referencias_laborales_validadas",
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    comentario_adicional = models.TextField(null=True, blank=True)

    observaciones_veracidad_documentos = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "cli_088_referencias_laborales"
        verbose_name = "REFERENCIAS LABORALES (VALIDACIÓN)"
        verbose_name_plural = "REFERENCIAS LABORALES (VALIDACIONES)"

    def __str__(self):
        return f"Referencias laborales #{self.id} (reporte 087 {self.reporte_accion_decisiva_087_id})"

