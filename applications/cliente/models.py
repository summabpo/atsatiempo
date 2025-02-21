from django.db import models
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# Create your models here.
class Cli051Cliente(models.Model):

    TIPO_CLIENTE = [
        ('1', 'empresa'),
        ('2', 'headhunter'),
        ('3', 'cliente_empresa'),
    ]

    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    nit = models.IntegerField(blank=False)
    razon_social = models.CharField(max_length=100, blank=False)
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004')
    email = models.EmailField(unique=True)
    contacto = models.CharField(max_length=50, blank=False)
    telefono = models.CharField(max_length=20, blank=False)
    perfil_empresarial = models.TextField(blank=True)  # Nuevo campo de texto
    logo = models.ImageField(upload_to='cliente', blank=True, null=True)  # Nuevo campo de imagen
    tipo_cliente = models.CharField(max_length=1, choices=TIPO_CLIENTE, default='1')

    def __str__(self):
        return self.razon_social + ' - ' + str(self.nit)
    class Meta:
        
        db_table = 'cli_051_cliente'

        verbose_name = 'CLIENTE'
        verbose_name_plural = 'CLIENTES'

class Cli058Pregunta(models.Model):
    cliente = models.ForeignKey('CLI051Cliente', on_delete=models.CASCADE)
    pregunta = models.TextField(blank=True)
    respuesta = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        blank=True
    )
    pregunta_correlacion = models.TextField(blank=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.SET_DEFAULT, default=1)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        
        db_table = 'cli_058_pregunta'

        verbose_name = 'PREGUNTA'
        verbose_name_plural = 'PREGUNTAS'

class Cli059Cuestionario(models.Model):
    titulo_cuestionario = models.TextField()
    fecha_creacion = models.DateField(auto_now_add=True)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.SET_DEFAULT, default=1)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        db_table = 'cli_059_cuestionario'

        verbose_name = 'CUESTIONARIO'
        verbose_name_plural = 'CUESTIONARIOS'

class Cli060CuestionarioPregunta(models.Model):
    id = models.BigAutoField(primary_key=True)
    cli059cuestionario = models.ForeignKey(Cli059Cuestionario, models.DO_NOTHING)
    cli058pregunta = models.ForeignKey(Cli058Pregunta, models.DO_NOTHING)
    fecha_asignacion = models.DateField(auto_now_add=True)

    class Meta:
        
        db_table = 'cli_060_cuestionario_pregunta'
        verbose_name = 'CUESTIONARIO_PREGUNTA'
        verbose_name_plural = 'CUESTIONARIOS_PREGUNTAS'
        unique_together = (('cli059cuestionario', 'cli058pregunta'),)

class Cli061AsignacionCandidatoCuestionario(models.Model):
    ESTADO_CHOICES = [
        ('p', 'Pendiente'),
        ('r', 'Realizado'),
    ]
    
    candidato = models.ForeignKey(Can101Candidato, on_delete=models.CASCADE)
    cuestionario = models.ForeignKey(Cli059Cuestionario, on_delete=models.CASCADE)
    estado_relacion = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='p')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'cli_061_asignacion_candidato_cuestionario'

        verbose_name = 'CUESTIONARIO'
        verbose_name_plural = 'CUESTIONARIOS'

class Cli062Respuesta(models.Model):
    asignacion = models.ForeignKey(Cli061AsignacionCandidatoCuestionario, on_delete=models.CASCADE)
    respuesta = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    pregunta = models.ForeignKey(Cli058Pregunta, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(default=timezone.now)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.SET_DEFAULT, default=1)
    candidato = models.ForeignKey(Can101Candidato, on_delete=models.CASCADE)

    def __str__(self):
        return f"Respuesta {self.id} para {self.pregunta}"
    
    class Meta:
        db_table = 'cli_062_respuesta'

        verbose_name = 'RESPUESTA'
        verbose_name_plural = 'RESPUESTAS'

class Cli064AsignacionCliente(models.Model):
    TIPO_ASIGNACION = [
        ('1', 'Asignación Cliente'),
        ('2', 'Asignación Headhunter'),
    ]

    id_cliente_maestro = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE, related_name='cliente_maestro')
    id_cliente_asignado = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE, related_name='cliente_asignado')
    fecha_asignacion = models.DateField(auto_now_add=True)
    tipo_asignacion = models.CharField(max_length=1, choices=TIPO_ASIGNACION, default='1')

    def __str__(self):
        return f"{self.id_cliente_maestro} asignado a {self.id_cliente_asignado}"

    class Meta:
        db_table = 'cli_064_asignacion_cliente'
        verbose_name = 'ASIGNACION_CLIENTE'
        verbose_name_plural = 'ASIGNACIONES_CLIENTES'
        unique_together = (('id_cliente_maestro', 'id_cliente_asignado'),)