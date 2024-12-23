from django.db import models

#modelos
from applications.usuarios.models import UsuarioBase
from applications.vacante.models import Cli056AplicacionVacante
from applications.common.models import Cat001Estado

# Create your models here.
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
        app_label = 'entrevista'
        # unique_together = ('asignacion_vacante', 'usuario_asignado', 'fecha_entrevista', 'hora_entrevista')  # Evita asignaciones duplicadas
