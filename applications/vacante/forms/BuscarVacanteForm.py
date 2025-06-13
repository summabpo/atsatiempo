from django import forms
from applications.services.choices import TIEMPO_EXPERIENCIA_CHOICES_STATIC
from applications.vacante.models import Cli052Vacante, Cli053SoftSkill, Cli054HardSkill, Cli055ProfesionEstudio, Cat004Ciudad
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from crispy_forms.layout import Div, HTML
from crispy_forms.bootstrap import PrependedText


class VacanteFiltro(forms.Form):
    

    salario_min = forms.CharField(
        label="Salario Minimo",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese salario mínimo'
        }),
        required=False
    )

    salario_max = forms.CharField(
        label="Salario Máximo",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese salario máximo'
        }),
        required=False
    )

    

    soft_skills = forms.ModelMultipleChoiceField(
        label='Habilidades Blandas',
        queryset=Cli053SoftSkill.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select form-select-lg form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione las habilidades',
            'data-allow-clear': 'true',
            'multiple': 'multiple'
        }),
        required=False
    )

    hard_skills = forms.ModelMultipleChoiceField(
        label='Habilidades Duras',
        queryset=Cli054HardSkill.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select form-select-lg form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione las habilidades',
            'data-allow-clear': 'true',
            'multiple': 'multiple'
        }),
        required=False
    )

    # hard_skills = forms.ModelMultipleChoiceField(
    #     label='HABILIDADES DURAS',
    #     queryset=Cli054HardSkill.objects.all(),
    #     widget=forms.CheckboxSelectMultiple(attrs={
    #         'class': 'form-check-input'
    #     }),
    #     required=False
    # )

    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_filtros'
        self.helper.form_method = 'get'

        # Campos del formulario
        self.fields['ciudad'] = forms.ChoiceField(
            label='Ciudad',
            choices=[('', 'Seleccione una ciudad')] + [(ciudad.id, ciudad.nombre) for ciudad in Cat004Ciudad.objects.all()],
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }),
            required=False
        )

        
        self.fields['experiencia_requerida'] = forms.ChoiceField(
            label='Experiencia Requerida',
            choices=TIEMPO_EXPERIENCIA_CHOICES_STATIC,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
            }),
            required=False
        )

        profesion_estudio_opciones = [('', 'Seleccione una Profesión o Estudio')] + [(profesion_estudio.id, profesion_estudio.nombre) for profesion_estudio in Cli055ProfesionEstudio.objects.all()]
        self.fields['profesion_estudio'] = forms.ChoiceField(
            label='Profesión o Estudio',
            choices=profesion_estudio_opciones,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
            }),
            required=False
        )

        


        self.helper.layout = Layout(
            # 🏗️ DATOS GENERALES
            Div(
            Div(
                HTML("<h5 class='mb-3 text-primary'>Buscar por:</h5>"),
                Div('ciudad', css_class='col-md-12'),             # ciudad
                Div('profesion_estudio', css_class='col-md-12'),  # profesion_estudio
                Div('experiencia_requerida', css_class='col-md-12'),  # profesion_estudio
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💼 DETALLES DEL TRABAJO
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Detalles del Trabajo</h4>"),
                Div('termino_contrato', css_class='col-3'),  # Término de contrato
                Div('tiempo_experiencia', css_class='col-3'),  # Tiempo de experiencia
                Div('modalidad', css_class='col-3'),  # Modalidad
                Div('jornada', css_class='col-3'),  # Jornada
                Div('horario_inicio', css_class='col-3'),  # Horario
                Div('horario_final', css_class='col-3'),  # Horario
                Div('hora_inicio', css_class='col-3'),  # Horario
                Div('hora_final', css_class='col-3'),  # Horario
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💼 LUGAR DEL TRABAJO
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Lugar de Trabajo</h4>"),
                Div('lugar_trabajo', css_class='col-6'),  # Lugar de trabajo
                Div('barrio', css_class='col-6'),  # Barrio
                Div('direccion', css_class='col-6'),  # Dirección
                Div('url_mapa', css_class='col-6'),  # URL del mapa
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 🛠️ REQUISITOS Y HABILIDADES
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Requisitos y Habilidades</h4>"),
                Div('soft_skills', css_class='col-6'),  # Habilidades blandas
                Div('hard_skills', css_class='col-6'),  # Habilidades duras
                Div('idioma', css_class='col-6'),  # Idioma
                Div('nivel_idioma', css_class='col-6'),  # nivel_idioma
                Div('profesion_estudio', css_class='col-6'),  # Profesión o estudio
                Div('nivel_estudio', css_class='col-4'),  # Nivel de estudio
                Div('estado_estudio', css_class='col-2'),  # Estado de estudio
                Div('edad_inicial', css_class='col-3'),  # Edad Inicial
                Div('edad_final', css_class='col-3'),  # Edad Final
                Div('genero', css_class='col-6'),  # genero
                Div('estudios_complementarios', css_class='col-9'),  # estudios_complementarios
                Div('estudios_complementarios_certificado', css_class='col-3'),  # estudios_complementarios_certificado
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💰 INFORMACIÓN SALARIAL
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Información Salarial</h4>"),
                Div(
                PrependedText('salario', '$', placeholder='0.00'),
                css_class='col-6'
                ),  # Salario
                Div('tipo_salario', css_class='col-6'),  # Tipo de salario
                Div('frecuencia_pago', css_class='col-6'),  # Frecuencia de pago
                Div(
                PrependedText('salario_adicional', '$', placeholder='0.00'),
                css_class='col-6'
                ),
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 📑 RESPONSABILIDADES DEL CARGO
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Responsabilidades del Cargo</h4>"),
                Div('funciones_responsabilidades', css_class='col-12'),  # Funciones y responsabilidades
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 🏗️ DESCRIPCION DE LA VACANTE
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Descripción de la Vacante</h4>"),
                Div('descripcion_vacante', css_class='col-12'),  # Número de vacantes
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

        # self.helper.layout = Layout(
        #     Fieldset(
        #         Row(
        #             Column('ciudad', css_class='form-group col-md-6 mb-0'),
        #             Column('profesion_estudio', css_class='form-group col-md-6 mb-0'),
        #             css_class='form-row'
        #         ),
        #     ),
        #     Fieldset(
        #         Row(
        #             Column('salario_min', css_class='form-group col-md-6 mb-0'),
        #             Column('salario_max', css_class='form-group col-md-6 mb-0'),
        #             css_class='form-row'
        #         ),
                
        #     ),
        # )
