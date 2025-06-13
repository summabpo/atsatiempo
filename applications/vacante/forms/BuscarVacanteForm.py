from django import forms
from applications.services.choices import TIEMPO_EXPERIENCIA_CHOICES_STATIC
from applications.vacante.models import Cli052Vacante, Cli053SoftSkill, Cli054HardSkill, Cli055ProfesionEstudio, Cat004Ciudad, Cli073PerfilVacante
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


        ciudades_filtradas = Cli073PerfilVacante.objects.filter(
            # Condición 1: El estado del perfil debe ser 1 (Activo)
            estado=1,
            # Condición 2: El perfil debe estar ligado a una vacante con estado 1 o 2
            cli052vacante__estado_vacante__in=[1, 2]
        ).values_list(
            'lugar_trabajo__id',      # CAMBIO: Ahora pedimos el ID de la ciudad
            'lugar_trabajo__nombre'   # CAMBIO: Ahora pedimos el nombre de la ciudad
        ).distinct().order_by('lugar_trabajo__nombre')

        ciudades_filtradas = [('', 'Seleccione una ciudad')] + list(ciudades_filtradas)

        # Campos del formulario
        self.fields['ciudad'] = forms.ChoiceField(
            label='Ciudad',
            choices=ciudades_filtradas,
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

        profesiones_en_uso = Cli073PerfilVacante.objects.filter(
            estado=1,
            cli052vacante__estado_vacante__in=[1, 2]
        ).values_list(
            'profesion_estudio__id',
            'profesion_estudio__nombre'
        ).distinct().order_by('profesion_estudio__nombre')
        
        profesion_estudio_opciones = [('', 'Seleccione una Profesión o Estudio')] + list(profesiones_en_uso)

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
            #  DATOS GENERALES
            Div(
            Div(
                HTML("<h5 class='mb-3 text-primary'>Buscar por:</h5>"),
                Div('ciudad', css_class='col-md-12'),             # ciudad
                Div('profesion_estudio', css_class='col-md-12'),  # profesion_estudio
                Div('experiencia_requerida', css_class='col-md-12'),  # Experiencvia Requerida
                # Div('salario_min', css_class='col-md-6'),        # Salario Minimo
                # Div('salario_max', css_class='col-md-6'),        # Salario Maximo
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )