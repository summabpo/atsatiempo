# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class Can101Candidato(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=254)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True, null=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True, null=True)
    sexo = models.CharField(max_length=1, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    telefono = models.CharField(max_length=10, blank=True, null=True)
    ciudad_id_004 = models.ForeignKey('Cat004Ciudad', models.DO_NOTHING, db_column='ciudad_id_004', blank=True, null=True)
    estado_id_001 = models.ForeignKey('Cat001Estado', models.DO_NOTHING, db_column='estado_id_001')

    class Meta:
        managed = False
        db_table = 'can_101_candidato'


class Can101CandidatoSkills(models.Model):
    id = models.BigAutoField(primary_key=True)
    nivel = models.IntegerField()
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101')
    skill_id_104 = models.ForeignKey('Can104Skill', models.DO_NOTHING, db_column='skill_id_104')

    class Meta:
        managed = False
        db_table = 'can_101_candidato_skills'


class Can102Experiencia(models.Model):
    id = models.BigAutoField(primary_key=True)
    entidad = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    fecha_inicial = models.DateField(blank=True, null=True)
    fecha_final = models.DateField()
    activo = models.BooleanField()
    logro = models.TextField(blank=True, null=True)
    cargo = models.CharField(max_length=100)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)
    estado_id_001 = models.ForeignKey('Cat001Estado', models.DO_NOTHING, db_column='estado_id_001')

    class Meta:
        managed = False
        db_table = 'can_102_experiencia'


class Can103Educacion(models.Model):
    id = models.BigAutoField(primary_key=True)
    institucion = models.CharField(max_length=100)
    fecha_inicial = models.DateField()
    fecha_final = models.DateField(blank=True, null=True)
    grado_en = models.BooleanField()
    titulo = models.CharField(max_length=100)
    carrera = models.CharField(max_length=100, blank=True, null=True)
    fortaleza_adquiridas = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)
    ciudad_id_004 = models.ForeignKey('Cat004Ciudad', models.DO_NOTHING, db_column='ciudad_id_004', blank=True, null=True)
    estado_id_001 = models.ForeignKey('Cat001Estado', models.DO_NOTHING, db_column='estado_id_001')

    class Meta:
        managed = False
        db_table = 'can_103_educacion'


class Can104Skill(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    estado_id_004 = models.ForeignKey('Cat001Estado', models.DO_NOTHING, db_column='estado_id_004')

    class Meta:
        managed = False
        db_table = 'can_104_skill'


class Cat001Estado(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    sigla = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cat_001_estado'


class Cat004Ciudad(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    departamento_id_003 = models.IntegerField(blank=True, null=True)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')

    class Meta:
        managed = False
        db_table = 'cat_004_ciudad'


class Cli051Cliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    nit = models.IntegerField()
    razon_social = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=254)
    contacto = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    perfil_empresarial = models.TextField()
    logo = models.CharField(max_length=100, blank=True, null=True)
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004')
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')

    class Meta:
        managed = False
        db_table = 'cli_051_cliente'


class Cli052Vacante(models.Model):
    id = models.BigAutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    numero_posiciones = models.IntegerField()
    experiencia_requerida = models.IntegerField()
    funciones_responsabilidades = models.TextField()
    salario = models.IntegerField(blank=True, null=True)
    estado_vacante = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    ciudad = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING)
    cliente_id_051 = models.ForeignKey(Cli051Cliente, models.DO_NOTHING)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING)
    profesion_estudio_id_055 = models.ForeignKey('Cli055ProfesionEstudio', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_052_vacante'


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


class Cli053SoftSkill(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_053_soft_skill'


class Cli054HardSkill(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_054_hard_skill'


class Cli055ProfesionEstudio(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_055_profesion_estudio'


class Cli056AplicacionVacante(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha_aplicacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()
    estado_aplicacion = models.IntegerField()
    candidato_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING)
    vacante_id_052 = models.ForeignKey(Cli052Vacante, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_056_aplicacion_vacante'
        unique_together = (('candidato_101', 'vacante_id_052'),)


class Cli057AsignacionEntrevista(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha_asignacion = models.DateTimeField()
    fecha_entrevista = models.DateField()
    hora_entrevista = models.TimeField()
    tipo_entrevista = models.CharField(max_length=1)
    lugar_enlace = models.CharField(max_length=255)
    estado_asignacion = models.IntegerField()
    estado = models.ForeignKey(Cat001Estado, models.DO_NOTHING)
    usuario_asignado = models.ForeignKey('Usuario', models.DO_NOTHING, blank=True, null=True)
    usuario_asigno = models.ForeignKey('Usuario', models.DO_NOTHING, related_name='cli057asignacionentrevista_usuario_asigno_set', blank=True, null=True)
    asignacion_vacante = models.ForeignKey(Cli056AplicacionVacante, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_057_asignacion_entrevista'
        unique_together = (('asignacion_vacante', 'usuario_asignado', 'fecha_entrevista', 'hora_entrevista'),)


class Cli058Pregunta(models.Model):
    id = models.BigAutoField(primary_key=True)
    pregunta = models.TextField()
    respuesta = models.IntegerField()
    pregunta_correlacion = models.TextField()
    fecha_creacion = models.DateField()
    cliente = models.ForeignKey(Cli051Cliente, models.DO_NOTHING)
    estado = models.ForeignKey(Cat001Estado, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_058_pregunta'


class Cli059Cuestionario(models.Model):
    id = models.BigAutoField(primary_key=True)
    titulo_cuestionario = models.TextField()
    fecha_creacion = models.DateField()
    estado = models.ForeignKey(Cat001Estado, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_059_cuestionario'


class Cli059CuestionarioPregunta(models.Model):
    id = models.BigAutoField(primary_key=True)
    cli059cuestionario = models.ForeignKey(Cli059Cuestionario, models.DO_NOTHING)
    cli058pregunta = models.ForeignKey(Cli058Pregunta, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_059_cuestionario_pregunta'
        unique_together = (('cli059cuestionario', 'cli058pregunta'),)


class Cli061AsignacionCandidatoCuestionario(models.Model):
    id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1)
    candidato = models.ForeignKey(Can101Candidato, models.DO_NOTHING)
    cuestionario = models.ForeignKey(Cli059Cuestionario, models.DO_NOTHING)
    estado_relacion = models.ForeignKey(Cat001Estado, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cli_061_asignacion_candidato_cuestionario'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('Usuario', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Grupo(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    activate = models.BooleanField()
    date = models.DateTimeField()
    description = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'grupo'


class GrupoPermiso(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha = models.DateTimeField()
    grupo = models.ForeignKey(Grupo, models.DO_NOTHING)
    permiso = models.ForeignKey('Permiso', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'grupo_permiso'
        unique_together = (('grupo', 'permiso'),)


class Permiso(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=255)
    descripcion = models.TextField()

    class Meta:
        managed = False
        db_table = 'permiso'


class TokenAutorizacion(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.CharField(unique=True, max_length=255)
    fecha_expiracion = models.DateTimeField()
    fecha_validacion = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Usuario', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'token_autorizacion'


class Usuario(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    primer_nombre = models.CharField(max_length=15)
    segundo_nombre = models.CharField(max_length=15)
    primer_apellido = models.CharField(max_length=15)
    segundo_apellido = models.CharField(max_length=15)
    telefono = models.CharField(max_length=15)
    is_verificado = models.BooleanField()
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, blank=True, null=True)
    cliente_id_051 = models.ForeignKey(Cli051Cliente, models.DO_NOTHING, blank=True, null=True)
    group = models.ForeignKey(Grupo, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'
