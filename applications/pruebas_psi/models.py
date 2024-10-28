from django.db import models
from applications.candidato.models import Can101Candidato
#from atsatiempo.asgi import application
class Psi201Pregunta(models.Model):
    FACTOR_CHOICES = [
        ('H', 'Honestidad-Humildad'),
        ('E', 'Emocionalidad'),
        ('X', 'Extraversión'),
        ('A', 'Amabilidad'),
        ('C', 'Escrupulosidad'),
        ('O', 'Apertura a la Experiencia'),
    ]

    SUBFACTOR_CHOICES = [
        # Subfactores de Honestidad-Humildad
        ('Sinceridad', 'Sinceridad'),
        ('Justicia', 'Justicia'),
        ('Evasión de la codicia', 'Evasión de la codicia'),
        ('Modestia', 'Modestia'),
        # Subfactores de Emocionalidad
        ('Miedo', 'Miedo'),
        ('Ansiedad', 'Ansiedad'),
        ('Dependencia', 'Dependencia'),
        ('Sentimentalidad', 'Sentimentalidad'),
        # Subfactores de Extraversión
        ('Seguridad social', 'Seguridad social'),
        ('Audacia social', 'Audacia social'),
        ('Sociabilidad', 'Sociabilidad'),
        ('Vitalidad', 'Vitalidad'),
        # Subfactores de Amabilidad
        ('Indulgencia', 'Indulgencia'),
        ('Suavidad', 'Suavidad'),
        ('Flexibilidad', 'Flexibilidad'),
        ('Paciencia', 'Paciencia'),
        # Subfactores de Escrupulosidad
        ('Organización', 'Organización'),
        ('Diligencia', 'Diligencia'),
        ('Perfeccionismo', 'Perfeccionismo'),
        ('Prudencia', 'Prudencia'),
        # Subfactores de Apertura a la experiencia
        ('Apreciación estética', 'Apreciación estética'),
        ('Curiosidad', 'Curiosidad'),
        ('Creatividad', 'Creatividad'),
        ('Inusualidad', 'Inusualidad'),
    ]

    id_pregunta = models.IntegerField(primary_key=True)
    texto = models.CharField(max_length=255, blank=True, null=True)
    es_invertida = models.BooleanField(blank=True, null=True)
    factor = models.CharField(max_length=1, blank=True, null=True)
    subfactor = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.texto

    class Meta:
        managed = False
        db_table = 'psi_201_pregunta'

class Psi202Respuesta(models.Model):
    id_respuesta = models.IntegerField(primary_key=True)
    candidato = models.ForeignKey(Can101Candidato, models.DO_NOTHING, db_column='candidato', blank=True, null=True)
    id_pregunta = models.ForeignKey(Psi201Pregunta, models.DO_NOTHING, db_column='id_pregunta', blank=True, null=True)
    respuesta = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.candidato} - {self.id_pregunta.texto}: {self.respuesta}"

    class Meta:
        managed = False
        db_table = 'psi_202_respuesta'