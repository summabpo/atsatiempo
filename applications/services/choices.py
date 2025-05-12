from django.db import models

NIVEL_CHOICHES_STATIC = [('', 'Seleccione una opción...')] + [
    ('B', 'BASICO'),
    ('I', 'INTERMEDIO'),
    ('S', 'SUPERIOR'),
]

TIPO_CLIENTE_STATIC = [('', 'Seleccione una opción...')] + [
        ('1', 'Cliente Standard'),
        ('2', 'Cliente Headhunter'),
        ('3', 'Cliente Asignado Headhunter'),
    ]

PAGO_NOMINA_STATIC = [('', 'Seleccione una opción...')] + [
        ('', 'Sin Definir'),
        ('1', 'Semanal'),
        ('2', 'Quincenal'),
        ('3', 'Mensual'),
    ]

ESTADO_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
        ('p', 'Pendiente'),
        ('r', 'Realizado'),
    ]

TIPO_ASIGNACION_STATIC = [('', 'Seleccione una opción...')] + [
        ('1', 'Asignación Cliente'),
        ('2', 'Asignación Headhunter'),
    ]

GENERO_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('S', 'Sin Especificar'),
    ('M', 'Masculino'),
    ('F', 'Femenino'),
]

MODALIDAD_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('R', 'Remoto'),
    ('P', 'Presencial'),
    ('H', 'Hibrido'),
]

JORNADA_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('T', 'Diurna'),   
    ('P', 'Nocturna'),
    ('R', 'Rotativa'),
]

TIPO_SALARIO_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('F', 'Fijo'),
    ('M', 'Mixto'),
    ('I', 'Integral'),
    ('H', 'Por Hora'),
]

TERMINO_CONTRATO_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('F', 'Fijo'),
    ('I', 'Indefinido'),
    ('O', 'Obra Labor'),
]

EDAD_CHOICES_STATIC = [('', 'Seleccione una opción... ')] + [
    ('7', 'Sin especificar'),
    ('1', '18-24 años'),
    ('2', '25-29 años'),
    ('3', '30-34 años'),
    ('4', '35-39 años'),
    ('5', '40-44 años'),
    ('6', '45-50 años'),
]

TIEMPO_EXPERIENCIA_CHOICES_STATIC = [('', 'Seleccione una opción... ')] + [
    (6, 'Sin Experiencia'),
    (1, '1 año'),
    (2, '2 años'),
    (3, '3 años'),
    (4, '4 años'),
    (5, '5 años o más'),
]

FRECUENCIA_PAGO_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('S', 'Semanal'),
    ('Q', 'Quincenal'),
    ('M', 'Mensual'),
]

NIVEL_ESTUDIO_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('1', 'Sin estudios'),
    ('2', 'Primaria'),
    ('3', 'Secundaria/Bachillerato'),
    ('4', 'Técnico'),
    ('5', 'Tecnólogo'),
    ('6', 'Universitario'),
    ('7', 'Postgrado'),
]

HORARIO_CHOICES_STATIC =  [('', 'Seleccione una opción...')] + [
    ('L', 'Lunes'),
    ('M', 'Martes'),
    ('X', 'Miércoles'),
    ('J', 'Jueves'),
    ('V', 'Viernes'),
    ('S', 'Sábado'),
    ('D', 'Domingo'),
]

ESTADO_VACANTE_CHOICHES_STATIC = [
    (1, 'Activa'),
    (2, 'En Proceso'),
    (3, 'Finalizada'),
    (4, 'Cancelada'),
]

NIVEL_IDIOMA_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('A1', 'A1 - Principiante'),
    ('A2', 'A2 - Básico'),
    ('B1', 'B1 - Intermedio'),
    ('B2', 'B2 - Intermedio Alto'),
    ('C1', 'C1 - Avanzado'),
    ('C2', 'C2 - Nativo o Bilingüe'),
]

IDIOMA_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('ES', 'Español'),
    ('EN', 'Inglés'),
    ('FR', 'Francés'),
    ('DE', 'Alemán'),
    ('IT', 'Italiano'),
    ('PT', 'Portugués'),
    ('RU', 'Ruso'),
    ('ZH', 'Chino'),
    ('JP', 'Japonés'),
    ('AR', 'Árabe'),
    ('OT', 'Otro'),
]

EDAD_SELECT_CHOICES_STATIC = [('', 'Seleccione una opción... ')] + [
    (str(age), f'{age} años') for age in range(18, 51)
]

NIVEL_HABILIDAD_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    (1, 'Básico'),
    (2, 'Intermedio'),
    (3, 'Superior'),
]
