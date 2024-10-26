# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Psi201Pregunta(models.Model):
    id_pregunta = models.SmallIntegerField(primary_key=True)
    texto = models.CharField(max_length=255, blank=True, null=True)
    es_invertida = models.BooleanField(blank=True, null=True)
    factor = models.CharField(max_length=1, blank=True, null=True)
    subfactor = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'psi_201_pregunta'


class Psi202Respuesta(models.Model):
    id_respuesta = models.IntegerField(primary_key=True)
    candidato_id_101 = models.ForeignKey('Can101Candidato', models.DO_NOTHING, db_column='candidato_id_101', blank=True, null=True)
    id_pregunta = models.ForeignKey(Psi201Pregunta, models.DO_NOTHING, db_column='id_pregunta', blank=True, null=True)
    respuesta = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'psi_202_respuesta'
