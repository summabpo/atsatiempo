from django import forms
from django.utils.html import format_html
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Div, HTML, Field
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
        modal_id = kwargs.pop('modal_id', None)  # ID del modal para dropdown-parent
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_crear_entrevista'
        self.helper.form_class = 'w-200'
        self.helper.form_tag = False  # No generar el tag <form> ya que está en el modal
        self.helper.disable_csrf = True  # El CSRF ya está en el form del modal

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
        # Configurar dropdown-parent según el modal proporcionado o usar el default
        dropdown_parent = f'#{modal_id}' if modal_id else '#modalEntrevista'
        self.fields['entrevistador'] = forms.ChoiceField(
            choices=usuario_choices,
            label='Entrevistador',
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-dropdown-parent': dropdown_parent,
            })
        )
        
        # Actualizar también el campo tipo_entrevista si hay modal_id
        if modal_id:
            self.fields['tipo_entrevista'].widget.attrs['data-dropdown-parent'] = dropdown_parent
        
        self.helper.layout = Layout(
            # DATOS DE LA ENTREVISTA
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Datos de la Entrevista</h4>"),
                    Div('fecha_entrevista', css_class='col-6 mb-3'),
                    Div('hora_entrevista', css_class='col-6 mb-3'),
                    Div('entrevistador', css_class='col-12 mb-3'),
                    Div('tipo_entrevista', css_class='col-12 mb-3'),
                    Div('lugar_enlace', css_class='col-12 mb-3'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
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
        # (4, 'Seleccionado'),
        # (5, 'Cancelado'),
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

    # 4. PRUEBAS (Resultados y análisis psicotécnicos)
    prueba_calificacion = forms.ChoiceField(
        choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
        label='Calificar',
        required=True,
        help_text='Escala del 1 al 10',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
        })
    )
    prueba_observaciones = forms.CharField(
        label='Observaciones',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Observaciones sobre resultados y análisis psicotécnicos...',
            'rows': 3,
            'cols': 30,
            'class': 'form-control form-control-solid',
        }),
    )
    prueba_cargada = forms.FileField(
        label='Cargar prueba (resultados/análisis psicotécnicos)',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control form-control-solid', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
    )

    # 5. INDICE Y CONFIABILIDAD DEL RIESGO
    confiabilidad_riesgo_calificacion = forms.ChoiceField(
        choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
        label='Calificar',
        required=True,
        help_text='Escala del 1 al 10',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
        })
    )
    confiabilidad_riesgo_observaciones = forms.CharField(
        label='Observaciones',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Observaciones sobre índice y confiabilidad del riesgo...',
            'rows': 3,
            'cols': 30,
            'class': 'form-control form-control-solid',
        }),
    )
    confiabilidad_riesgo_cargado = forms.FileField(
        label='Cargar documento (índice y confiabilidad del riesgo)',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control form-control-solid', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
    )

    def __init__(self, *args, **kwargs):
        habilidades = kwargs.pop('habilidades', None) or []
        fit_cultural = kwargs.pop('fit_cultural', None) or []
        motivadores = kwargs.pop('motivadores', None) or []
        super().__init__(*args, **kwargs)

        # Campos dinámicos: observaciones + calificación (Select2) por cada habilidad de la vacante
        self.habilidades_list = list(habilidades)
        for h in self.habilidades_list:
            obs_name = f'habilidad_{h.id}_observacion'
            cal_name = f'habilidad_{h.id}'
            self.fields[obs_name] = forms.CharField(
                label='Observaciones',
                required=False,
                widget=forms.Textarea(attrs={
                    'placeholder': f'Observaciones sobre {h.nombre}...',
                    'rows': 3,
                    'cols': 30,
                    'class': 'form-control form-control-solid',
                }),
            )
            self.fields[cal_name] = forms.ChoiceField(
                choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
                label='Calificar',
                required=True,
                help_text='Escala del 1 al 10',
                widget=forms.Select(attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                }),
            )

        # Campos dinámicos: calificación + observaciones por cada ítem de fit cultural de la vacante
        self.fit_cultural_list = list(fit_cultural)
        for fc in self.fit_cultural_list:
            obs_name = f'fit_cultural_{fc.id}_observacion'
            cal_name = f'fit_cultural_{fc.id}'
            self.fields[obs_name] = forms.CharField(
                label='Observaciones',
                required=False,
                widget=forms.Textarea(attrs={
                    'placeholder': f'Observaciones sobre {fc.nombre}...',
                    'rows': 3,
                    'cols': 30,
                    'class': 'form-control form-control-solid',
                }),
            )
            self.fields[cal_name] = forms.ChoiceField(
                choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
                label='Calificar',
                required=True,
                help_text='Escala del 1 al 10',
                widget=forms.Select(attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                }),
            )

        # Campos dinámicos: calificación + observaciones por cada motivador de la vacante
        self.motivadores_list = list(motivadores)
        for m in self.motivadores_list:
            obs_name = f'motivador_{m.id}_observacion'
            cal_name = f'motivador_{m.id}'
            self.fields[obs_name] = forms.CharField(
                label='Observaciones',
                required=False,
                widget=forms.Textarea(attrs={
                    'placeholder': f'Observaciones sobre {m.nombre}...',
                    'rows': 3,
                    'cols': 30,
                    'class': 'form-control form-control-solid',
                }),
            )
            self.fields[cal_name] = forms.ChoiceField(
                choices=[('', 'Seleccione...')] + [(i, str(i)) for i in range(1, 11)],
                label='Calificar',
                required=True,
                help_text='Escala del 1 al 10',
                widget=forms.Select(attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                }),
            )

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_gestion_entrevista'
        self.helper.form_class = 'w-200'

        layout_items = []

        # 1. MATCH 360 PREDICTIVO DEL TALENTO (HABILIDADES DE LA VACANTE) – título + habilidades
        if self.habilidades_list:
            habilidades_layout = [
                HTML("<h4 class='mb-3 text-primary'>1. MATCH 360 PREDICTIVCO DEL TALENTO (CONCEPTO DE LAS HABILIDADES)</h4>"),
                HTML("<p class='text-muted small mb-3'>Califique cada habilidad de 1 a 10 y agregue observaciones según lo observado en la entrevista.</p>"),
            ]
            for i, h in enumerate(self.habilidades_list):
                if i > 0:
                    habilidades_layout.append(HTML('<hr class="my-4">'))
                habilidades_layout.append(HTML(format_html('<p class="mb-2 fw-bold text-uppercase">{}</p>', h.nombre)))
                habilidades_layout.append(Div(f'habilidad_{h.id}', css_class='col-12 mb-2'))
                habilidades_layout.append(Div(f'habilidad_{h.id}_observacion', css_class='col-12 mb-4'))
            layout_items.append(
                Div(
                    Div(*habilidades_layout, css_class='row'),
                    css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
                )
            )

        # 2. FIT CULTURAL (ítems de la vacante: calificación + observaciones)
        if self.fit_cultural_list:
            fit_layout = [
                HTML("<h4 class='mb-3 text-primary'>2. FIT CULTURAL</h4>"),
                HTML("<p class='text-muted small mb-3'>Califique cada ítem de fit cultural de 1 a 10 y agregue observaciones según lo observado en la entrevista.</p>"),
            ]
            for i, fc in enumerate(self.fit_cultural_list):
                if i > 0:
                    fit_layout.append(HTML('<hr class="my-4">'))
                fit_layout.append(HTML(format_html('<p class="mb-2 fw-bold text-uppercase">{}</p>', fc.nombre)))
                fit_layout.append(Div(f'fit_cultural_{fc.id}', css_class='col-12 mb-2'))
                fit_layout.append(Div(f'fit_cultural_{fc.id}_observacion', css_class='col-12 mb-4'))
            layout_items.append(
                Div(
                    Div(*fit_layout, css_class='row'),
                    css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
                )
            )

        # 3. MOTIVADORES (ítems de la vacante: calificación + observaciones)
        if self.motivadores_list:
            motivadores_layout = [
                HTML("<h4 class='mb-3 text-primary'>3. MOTIVADORES</h4>"),
                HTML("<p class='text-muted small mb-3'>Califique cada motivador de 1 a 10 y agregue observaciones según lo observado en la entrevista.</p>"),
            ]
            for i, m in enumerate(self.motivadores_list):
                if i > 0:
                    motivadores_layout.append(HTML('<hr class="my-4">'))
                motivadores_layout.append(HTML(format_html('<p class="mb-2 fw-bold text-uppercase">{}</p>', m.nombre)))
                motivadores_layout.append(Div(f'motivador_{m.id}', css_class='col-12 mb-2'))
                motivadores_layout.append(Div(f'motivador_{m.id}_observacion', css_class='col-12 mb-4'))
            layout_items.append(
                Div(
                    Div(*motivadores_layout, css_class='row'),
                    css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
                )
            )

        layout_items.extend([
            # 4. PRUEBAS (Resultados y análisis psicotécnicos)
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>4. PRUEBAS (Resultados y análisis psicotécnicos)</h4>"),
                    HTML("<p class='text-muted small mb-3'>Califique de 1 a 10, agregue observaciones y opcionalmente cargue el archivo de resultados o análisis psicotécnicos.</p>"),
                    Div('prueba_calificacion', css_class='col-12 mb-2'),
                    Div('prueba_observaciones', css_class='col-12 mb-2'),
                    Div('prueba_cargada', css_class='col-12 mb-4'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            # 5. INDICE Y CONFIABILIDAD DEL RIESGO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>5. INDICE Y CONFIABILIDAD DEL RIESGO</h4>"),
                    HTML("<p class='text-muted small mb-3'>Califique de 1 a 10, agregue observaciones y opcionalmente cargue el documento de índice y confiabilidad del riesgo.</p>"),
                    Div('confiabilidad_riesgo_calificacion', css_class='col-12 mb-2'),
                    Div('confiabilidad_riesgo_observaciones', css_class='col-12 mb-2'),
                    Div('confiabilidad_riesgo_cargado', css_class='col-12 mb-4'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        ])

        layout_items.append(
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

        self.helper.layout = Layout(*layout_items)

        

    def clean(self):
        cleaned_data = super().clean()

        observacion = cleaned_data.get('observacion')
        estado_asignacion = cleaned_data.get('estado_asignacion')

        if not observacion:
            self.add_error('observacion', 'La observación no puede estar vacía.')

        if estado_asignacion == '':
            self.add_error('estado_asignacion', 'Debe seleccionar un estado.')

        return cleaned_data