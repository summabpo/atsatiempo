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
MOTIVO_VACANTE_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('PN', 'Posición nueva'),
    ('RE', 'Reemplazo'),
    ('LM', 'Licencia de maternidad'),
    ('OT', 'Otro'),
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
    ('8', 'Diplomado'),
    ('9', 'Curso'),
    
]

ESTADO_ESTUDIOS_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('G', 'Graduado'),
    ('C', 'En curso'),
    ('A', 'Aplazado'),
]


TIPO_HORARIO_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('HF', 'Horario Fijo'),
    ('HX', 'Horario Flexible'),
    ('HR', 'Horario Rotativo'),
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

TIPO_PROFESION_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    ('E', 'Profesión Específica'),
    ('G', 'Grupo de Profesiones'),
    ('L', 'Listado Personalizado'),
]

EDAD_SELECT_CHOICES_STATIC = [('', 'Seleccione una opción... ')] + [
    (str(age), f'{age} años') for age in range(18, 51)
]

NIVEL_HABILIDAD_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    (1, 'Básico'),
    (2, 'Intermedio'),
    (3, 'Superior'),
]


MOTIVO_SALIDA_CHOICES_STATIC =  [
    (1, 'Renuncia'),
    (2, 'Justa Causa'),
    (3, 'Terminación de Contrato')
]

TIPO_HABILIDAD_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
        ('S', 'Suave'),
        ('D', 'Técnica'),
    ]


ESTADO_APLICACION_CHOICES_STATIC = [
    (1, 'Aplicado'),
    (2, 'Entrevista Programada'),
    (3, 'Entrevista Aprobada'),
    (4, 'Entrevista No Aprobada'),
    (5, 'Prueba Programada'),
    (6, 'Prueba Superada'),
    (7, 'Prueba No Superada'),
    (8, 'Seleccionado'),
    (9, 'Finalizada'),
    (10, 'Cancelada'),
    (11, 'Desiste'),
    (12, 'No Apto'),
    (13, 'Seleccionado por Headhunter'),
]

ESTADO_APLICACION_COLOR_STATIC = {
    1: ('Aplicado', 'warning'),
    2: ('Entrevista Programada', 'info'),
    3: ('Entrevista Aprobada', 'success'),
    4: ('Entrevista No Aprobada', 'danger'),
    5: ('Prueba Programada', 'info'),
    6: ('Prueba Superada', 'success'),
    7: ('Prueba No Superada', 'danger'),
    8: ('Seleccionado', 'success'),
    9: ('Finalizada', 'primary'),
    10: ('Cancelada', 'secondary'),
    11: ('Desiste', 'secondary'),
    12: ('No Apto', 'danger'),
}

ESTADO_RECLUTADO_CHOICES_STATIC = [('', 'Seleccione una opción...')] + [
    (1, 'Recibido'),
    (2, 'Seleccionado'),
    (3, 'Finalizalista'),
    (4, 'Descartado'),
]

ESTADO_RECLUTADO_COLOR_STATIC = {
    1: ('Recibido', 'warning'),
    2: ('Seleccionado', 'success'),
    3: ('Finalizalista', 'primary'),
    4: ('Descartado', 'danger'),
}