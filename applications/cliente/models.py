from django.db import models # type: ignore
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato
from django.core.validators import MinValueValidator, MaxValueValidator # type: ignore
from django.utils import timezone # type: ignore


# Create your models here.
class Cli065ActividadEconomica(models.Model):
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    class Meta:
        db_table = 'cli_065_actividad_economica'
        verbose_name = 'ACTIVIDAD_ECONOMICA'
        verbose_name_plural = 'ACTIVIDADES_ECONOMICAS'

class Cli051Cliente(models.Model):

    TIPO_CLIENTE = [
        ('1', 'Cliente Standard'),
        ('2', 'Cliente Headhunter'),
        ('3', 'Cliente Asignado Headhunter'),
    ]

    PAGO_NOMINA = [
        ('', 'Sin Definir'),
        ('1', 'Semanal'),
        ('2', 'Quincenal'),
        ('3', 'Mensual'),
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
    actividad_economica = models.ForeignKey(Cli065ActividadEconomica, on_delete=models.CASCADE, null=True, blank=True)
    periodicidad_pago = models.CharField(max_length=1, choices=PAGO_NOMINA, default='1', blank=True, null=True)
    referencias_laborales = models.IntegerField(blank=True, null=True)
    cantidad_colaboradores = models.IntegerField(blank=True, null=True)
    contacto_cargo = models.CharField(max_length=100, blank=True, null=True)
    direccion_cargo = models.CharField(max_length=100, blank=True, null=True)



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
    estado = models.ForeignKey(Cat001Estado, models.DO_NOTHING, default=1)
    def __str__(self):
        return f"{self.id_cliente_maestro} asignado a {self.id_cliente_asignado}"

    class Meta:
        db_table = 'cli_064_asignacion_cliente'
        verbose_name = 'ASIGNACION_CLIENTE'
        verbose_name_plural = 'ASIGNACIONES_CLIENTES'
        unique_together = (('id_cliente_maestro', 'id_cliente_asignado'),)

class Cli066PruebasPsicologicas(models.Model):
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    uso = models.TextField(blank=True)
    cargos_recomendados = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'cli_066_pruebas_psicologicas'
        verbose_name = 'PRUEBA_PSICOLOGICA'
        verbose_name_plural = 'PRUEBAS_PSICOLOGICAS'

class Cli067PoliticasInternas(models.Model):
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'cli_067_politicas_internas'
        verbose_name = 'POLITICA_INTERNA'
        verbose_name_plural = 'POLITICAS_INTERNAS'

class Cli051ClientePruebas(models.Model):
    cliente = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE)
    prueba_psicologica = models.ForeignKey(Cli066PruebasPsicologicas, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField(auto_now_add=True)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.SET_DEFAULT, default=1)

    class Meta:
        db_table = 'cli_051_cliente_pruebas'
        unique_together = (('cliente', 'prueba_psicologica'),)  # Evita duplicados

    def __str__(self):
        return f"{self.cliente.razon_social} - {self.prueba_psicologica.nombre}"


class Cli051ClientePoliticas(models.Model):
    cliente = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE)
    politica_interna = models.ForeignKey(Cli067PoliticasInternas, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField(auto_now_add=True)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.SET_DEFAULT, default=1)

    class Meta:
        db_table = 'cli_051_cliente_politicas'
        unique_together = (('cliente', 'politica_interna'),)  # Evita duplicados

    def __str__(self):
        return f"{self.cliente.razon_social} - {self.politica_interna.nombre}"
    
class Cli068Cargo(models.Model):
    nombre_cargo = models.CharField(max_length=100)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, default=1)
    fecha_creado = models.DateField(auto_now_add=True)
    cliente = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_cargo

    class Meta:
        db_table = 'cli_068_cargos'
        verbose_name = 'CARGO'
        verbose_name_plural = 'CARGOS'

class Cli069Requisito(models.Model):
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    fecha_creado = models.DateField(auto_now_add=True)
    cliente = models.ForeignKey(Cli051Cliente, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre if self.nombre else "Requisito sin nombre"

    class Meta:
        db_table = 'cli_069_requisito'
        verbose_name = 'REQUISITO'
        verbose_name_plural = 'REQUISITOS'

class Cli070AsignacionRequisito(models.Model):
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cli068Cargo, on_delete=models.CASCADE)
    requisito = models.ForeignKey(Cli069Requisito, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'cli_070_asignacion_requisito'
        verbose_name = 'ASIGNACION_REQUISITO'
        verbose_name_plural = 'ASIGNACIONES_REQUISITOS'
        unique_together = (('cargo', 'requisito'),)

    def __str__(self):
        return f"{self.cargo.nombre_cargo} - {self.requisito.nombre}"

class Cli071AsignacionPrueba(models.Model):
    cargo = models.ForeignKey(Cli068Cargo, on_delete=models.CASCADE)
    cliente_prueba = models.ForeignKey(Cli051ClientePruebas, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField(auto_now_add=True)
    estado = models.ForeignKey(Cat001Estado, on_delete=models.CASCADE, default=1)

    class Meta:
        db_table = 'cli_071_asignacion_prueba'
        verbose_name = 'ASIGNACION_PRUEBA'
        verbose_name_plural = 'ASIGNACIONES_PRUEBAS'
        unique_together = (('cliente_prueba', 'cargo'),)

    def __str__(self):
        return f"{self.cliente_prueba} - {self.fecha_asignacion}"