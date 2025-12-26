from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Div, HTML
from applications.entrevista.models import Cli057AsignacionEntrevista
from applications.usuarios.models import UsuarioBase
from django.utils import timezone
from datetime import datetime, time


class EntrevistaCrearForm(forms.Form):
    # Campos del usuario
    fecha_entrevista = forms.DateField(
        label='Fecha de Entrevista',
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'type': 'date',
            'id': 'kt_datepicker_1'
        })
    )

    hora_entrevista = forms.TimeField(
        label='Hora de Entrevista',
        required=True,
        widget=forms.TimeInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'type': 'time',
            'id': 'kt_timepicker_1',
        })
    )

    tipo_entrevista = forms.ChoiceField(
        choices=Cli057AsignacionEntrevista.TIPO_ENTREVISTA,
        label='Tipo de Entrevista',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-dropdown-parent': '#modalEntrevista',
            'placeholder': 'Seleccione el tipo de entrevista',
        })
    )

    lugar_enlace = forms.CharField(
        label='Lugar o Enlace',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'placeholder': 'Ingrese el lugar o enlace de la entrevista',
        })
    )

    # entrevistador = forms.ModelChoiceField(
    #     queryset=UsuarioBase.objects.none(),  # Inicialmente vacío, se actualizará en __init__
    #     label='Cliente',
    #     required=False,
    #     widget=forms.Select(attrs={
    #         'class': 'form-select form-select-solid',
    #         'data-control': 'select2',
    #     })
    # )

    def __init__(self, *args, **kwargs):
        grupo_id = kwargs.pop('grupo_id', None)
        cliente_id = kwargs.pop('cliente_id', None)
        vacante = kwargs.pop('vacante', None)
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_crear_entrevista'
        self.helper.form_class = 'w-200'

        usuario_choices = [('', '----------')]
        
        # Obtener analistas asignados a la vacante (grupo 5)
        analistas_ids = set()
        
        # Analista principal asignado
        if vacante and vacante.usuario_asignado_id:
            analistas_ids.add(vacante.usuario_asignado_id)
        
        # Analistas del JSON data_asignacion_usuario
        if vacante and vacante.data_asignacion_usuario:
            if isinstance(vacante.data_asignacion_usuario, list):
                for asignacion in vacante.data_asignacion_usuario:
                    if isinstance(asignacion, dict) and 'usuario_id' in asignacion:
                        analistas_ids.add(asignacion['usuario_id'])
        
        # Obtener los analistas asignados
        if analistas_ids:
            analistas = UsuarioBase.objects.filter(
                id__in=analistas_ids,
                is_active=True
            ).order_by('primer_apellido')
            
            if analistas.exists():
                usuario_choices.append(('', '--- ANALISTAS ASIGNADOS ---'))
                for analista in analistas:
                    usuario_choices.append((analista.id, f" {analista.primer_apellido} {analista.primer_nombre} (Analista)"))
        
        # Obtener entrevistadores del grupo 4
        entrevistadores = UsuarioBase.objects.filter(
            group=4,
            cliente_id_051=cliente_id,
            is_active=True
        ).order_by('primer_apellido')
        
        if entrevistadores.exists():
            usuario_choices.append(('', '--- ENTREVISTADORES ---'))
            for entrevistador in entrevistadores:
                usuario_choices.append((entrevistador.id, f" {entrevistador.primer_apellido} {entrevistador.primer_nombre}"))
        
        # Añadir el campo entrevistador al formulario con las opciones obtenidas
        self.fields['entrevistador'] = forms.ChoiceField(
            choices=usuario_choices,
            label='Entrevistador',
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-dropdown-parent': '#modalEntrevista',
            })
        )
        
        self.helper.layout = Layout(
                Row(
                    Column('fecha_entrevista', css_class='form-group mb-0'),
                    Column('hora_entrevista', css_class='form-group mb-0'),
                ),
                Row(
                    Column('entrevistador', css_class='form-group mb-0'),
                    css_class='fw-semibold fs-6 mb-2'
                ),
                Row(
                    Column('tipo_entrevista', css_class='form-group mb-0'),
                    css_class='fw-semibold fs-6 mb-2'
                ),
                Row(
                    Column('lugar_enlace', css_class='form-group mb-0'),
                    css_class='fw-semibold fs-6 mb-2'
                ),
            )

    def clean(self):
        cleaned_data = super().clean()

        fecha_entrevista = cleaned_data.get('fecha_entrevista')
        hora_entrevista = cleaned_data.get('hora_entrevista')

        # Verificar si es una cadena y convertirla a un objeto datetime
        if isinstance(fecha_entrevista, str):
            fecha_entrevista = datetime.strptime(fecha_entrevista, "%Y-%m-%d").date()

        # valida fecha
        if fecha_entrevista:
            fecha_actual = timezone.now().date()
            if fecha_entrevista < fecha_actual:
                self.add_error('fecha_entrevista', 'La fecha de la entrevista no puede ser anterior a la fecha actual.')

        return cleaned_data
    
class EntrevistaGestionForm(forms.Form):
    ESTADO_ASIGNACION = [
        (0, '----'),
        (2, 'Apto'),
        (3, 'No Apto'),
        (4, 'Seleccionado'),
        (5, 'Cancelado'),
    ]

    observacion = forms.CharField(
        label='Observaciones',
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Describa el motivo de su califiación',
                'rows': 5,  
                'cols': 30,  
                'class': 'fixed-size-textarea form-control-solid'
            }
        )
    )

    estado_asignacion = forms.ChoiceField(
        choices=[('', 'Seleccione...')] + list(ESTADO_ASIGNACION),
        label='Calificar',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
        })
    )

    identidad_descripcion = forms.CharField(
        label='¿Quién es esta persona más allá de su hoja de vida?',
        required=True,
        help_text='Enfoque: esencia humana, valores visibles, forma de relacionarse, nivel de autenticidad y coherencia interna.',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Describa quién es esta persona más allá de su hoja de vida...',
                'rows': 5,
                'cols': 30,
                'class': 'form-control form-control-solid'
            }
        )
    )

    identidad_calificacion = forms.ChoiceField(
        choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
        label='Calificación',
        required=True,
        help_text='Escala del 1 al 10',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
        })
    )

    # 2. ANÁLISIS CORPORAL – Lenguaje no verbal
    analisis_corporal_observaciones = forms.CharField(
        label='Observaciones breves',
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Ingrese observaciones breves sobre el lenguaje no verbal...',
                'rows': 4,
                'cols': 30,
                'class': 'form-control form-control-solid'
            }
        )
    )

    analisis_corporal_calificacion = forms.ChoiceField(
        choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
        label='Calificación',
        required=True,
        help_text='Escala del 1 al 10',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
        })
    )

    # 3. PROPÓSITO Y CRECIMIENTO PERSONAL
    proposito_descripcion = forms.CharField(
        label='Descripción breve del propósito y evolución personal',
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Describa el propósito y evolución personal...',
                'rows': 4,
                'cols': 30,
                'class': 'form-control form-control-solid'
            }
        )
    )

    proposito_calificacion = forms.ChoiceField(
        choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
        label='Calificación',
        required=True,
        help_text='Escala del 1 al 10',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
        })
    )

    # 4. ANÁLISIS 360° DE ENCAJE PERSONAL Y PROFESIONAL
    encaje_360_observaciones = forms.CharField(
        label='Observaciones',
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Ingrese observaciones sobre el encaje personal y profesional...',
                'rows': 4,
                'cols': 30,
                'class': 'form-control form-control-solid'
            }
        )
    )

    encaje_360_calificacion = forms.ChoiceField(
        choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
        label='Calificación',
        required=True,
        help_text='Escala del 1 al 10',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
        })
    )

    # 5. INDICE DE CONFIABILIDAD Y RIESGO
    confiabilidad_riesgo_calificacion = forms.ChoiceField(
        choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
        label='Calificación',
        required=True,
        help_text='Escala del 1 al 10',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_gestion_entrevista' 
        self.helper.form_class = 'w-200'
    
        self.helper.layout = Layout(
            # 1. IDENTIDAD MÁS ALLÁ DEL CV
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>1. IDENTIDAD MÁS ALLÁ DEL CV </h4>"),
                    Div('identidad_descripcion', css_class='col-12 mb-3'),
                    Div('identidad_calificacion', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            # 2. ANÁLISIS CORPORAL – Lenguaje no verbal
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>2. ANÁLISIS CORPORAL – Lenguaje no verbal</h4>"),
                    Div('analisis_corporal_observaciones', css_class='col-12 mb-3'),
                    Div('analisis_corporal_calificacion', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            # 3. PROPÓSITO Y CRECIMIENTO PERSONAL
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>3. PROPÓSITO Y CRECIMIENTO PERSONAL</h4>"),
                    Div('proposito_descripcion', css_class='col-12 mb-3'),
                    Div('proposito_calificacion', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            # 4. ANÁLISIS 360° DE ENCAJE PERSONAL Y PROFESIONAL
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>4. ANÁLISIS 360° DE ENCAJE PERSONAL Y PROFESIONAL</h4>"),
                    Div('encaje_360_observaciones', css_class='col-12 mb-3'),
                    Div('encaje_360_calificacion', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            # 5. INDICE DE CONFIABILIDAD Y RIESGO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>5. INDICE DE CONFIABILIDAD Y RIESGO</h4>"),
                    Div('confiabilidad_riesgo_calificacion', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            # CALIFICACIÓN GENERAL
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Calificación General</h4>"),
                    Div('estado_asignacion', css_class='col-12 mb-3'),
                    Div('observacion', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

        

    def clean(self):
        cleaned_data = super().clean()

        observacion = cleaned_data.get('observacion')
        estado_asignacion = cleaned_data.get('estado_asignacion')

        if not observacion:
            self.add_error('observacion', 'La observación no puede estar vacía.')

        if estado_asignacion == '':
            self.add_error('estado_asignacion', 'Debe seleccionar un estado.')

        return cleaned_data