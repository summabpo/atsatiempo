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
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Can101Candidato(models.Model):
    estado_id_001 = models.ForeignKey('Cat001Estado', models.DO_NOTHING, db_column='estado_id_001')
    email = models.IntegerField()
    primer_nombre = models.TextField(blank=True, null=True)
    segundo_nombre = models.TextField(blank=True, null=True)
    primer_apellido = models.TextField(blank=True, null=True)
    segundo_apellido = models.TextField(blank=True, null=True)
    ciudad_id_004 = models.ForeignKey('Cat004Ciudad', models.DO_NOTHING, db_column='ciudad_id_004', blank=True, null=True)
    sexo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'can_101_candidato'


class Can102Experiencia(models.Model):
    estado_id_001 = models.ForeignKey('Cat001Estado', models.DO_NOTHING, db_column='estado_id_001')
    entidad = models.TextField()
    sector = models.TextField()
    fecha_inicial = models.TextField()
    fecha_final = models.TextField(blank=True, null=True)
    activo = models.IntegerField()
    logro = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'can_102_experiencia'


class Can103Educacion(models.Model):
    estado_id_001 = models.ForeignKey('Cat001Estado', models.DO_NOTHING, db_column='estado_id_001')
    institucion = models.TextField()
    fecha_inicial = models.TextField()
    fecha_final = models.TextField()
    grado_en = models.TextField(blank=True, null=True)
    titulo = models.TextField(blank=True, null=True)
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'can_103_educacion'


class Can104Skill(models.Model):
    estado_id_004 = models.ForeignKey('Cat001Estado', models.DO_NOTHING, db_column='estado_id_004')
    nombre = models.TextField()

    class Meta:
        managed = False
        db_table = 'can_104_skill'


class Can105SkillCandidato(models.Model):
    candidato_id_101 = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato_id_101')
    skill_id_104 = models.ForeignKey(Can104Skill, models.DO_NOTHING, db_column='skill_id_104')

    class Meta:
        managed = False
        db_table = 'can_105_skill_candidato'


class Cat001Estado(models.Model):
    nombre = models.TextField()
    sigla = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cat_001_estado'


class Cat004Ciudad(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    nombre = models.TextField()
    departamento_id_003 = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cat_004_ciudad'


class Cli051Cliente(models.Model):
    estado_id_001 = models.ForeignKey(Cat001Estado, models.DO_NOTHING, db_column='estado_id_001')
    nit = models.IntegerField()
    razon_social = models.TextField()
    ciudad_id_004 = models.ForeignKey(Cat004Ciudad, models.DO_NOTHING, db_column='ciudad_id_004')
    email = models.TextField()

    class Meta:
        managed = False
        db_table = 'cli_051_cliente'


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

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
