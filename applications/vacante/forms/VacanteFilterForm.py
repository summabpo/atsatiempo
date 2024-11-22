from django import forms
from applications.vacante.models import Cli052Vacante, Cli053SoftSkill, Cli054HardSkill, Cli055ProfesionEstudio, Cat004Ciudad
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset


class VacanteFilterForm(forms.Form):
    EXPERIENCIA_TIEMPO = [
        ('', 'Seleccione una opción... '),
        (1, '0 a 6 Meses'),
        (2, '1 año a 2 años'),
        (3, 'Más de 2 años'),
        (4, 'Sin experiencia'),
    ]

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

        experiencia_opciones = [('', '---------')] + Cli052Vacante.EXPERIENCIA_TIEMPO
        self.fields['experiencia_requerida'] = forms.ChoiceField(
            label='Experiencia',
            choices=experiencia_opciones,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',
            }),
            required=False
        )

        profesion_estudio_opciones = [('', 'Seleccione una Profesión o Estudio')] + [(profesion_estudio.id, profesion_estudio.nombre) for profesion_estudio in Cli055ProfesionEstudio.objects.all()]
        self.fields['profesion_estudio'] = forms.ChoiceField(
            label='Profesión o Estudio',
            choices=profesion_estudio_opciones,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }),
            required=False
        )

        self.helper.layout = Layout(
            Fieldset(
                'Filtros',
                Row(
                    Column('ciudad', css_class='form-group col-md-12 mb-10'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Salario',
                Row(
                    Column('salario_min', css_class='form-group col-md-6 mb-5'),
                    Column('salario_max', css_class='form-group col-md-6 mb-10'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Habilidades Blandas',
                Row(
                    Column('soft_skills', css_class='form-group col-md-12 mb-10'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Habilidades Duras',
                Row(
                    Column('hard_skills', css_class='form-group col-md-12 mb-10'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Profesión o Estudio',
                Row(
                    Column('profesion_estudio', css_class='form-group col-md-12 mb-10'),
                    css_class='form-row'
                ),
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
