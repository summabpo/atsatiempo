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

    # Campos del formulario
    ciudad = forms.ChoiceField(
        label='CIUDAD',
        choices=[('', 'Seleccione una ciudad')] + [(ciudad.id, ciudad.nombre) for ciudad in Cat004Ciudad.objects.all()],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
        }),
        required=False
    )

    salario_min = forms.CharField(
        label="SALARIO MÍNIMO",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese salario mínimo'
        }),
        required=False
    )

    salario_max = forms.CharField(
        label="SALARIO MÁXIMO",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese salario máximo'
        }),
        required=False
    )

    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_filtros'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(
                    Column('ciudad', css_class='form-group col-md-6 mb-0'),
                    Column('profesion_estudio', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('salario_min', css_class='form-group col-md-6 mb-0'),
                    Column('salario_max', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                
            ),
        )
