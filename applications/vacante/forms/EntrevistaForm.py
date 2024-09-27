from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from applications.vacante.models import Cli057AsignacionEntrevista


class EntrevistaCrearForm(forms.Form):
    # Campos del usuario
    fecha_entrevista = forms.DateField(
        label='Fecha de Entrevista',
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'type': 'date',
        })
    )

    hora_entrevista = forms.TimeField(
        label='Hora de Entrevista',
        required=True,
        widget=forms.TimeInput(attrs={
            'class': 'form-control form-control-solid mb-3 mb-lg-0',
            'type': 'time',
        })
    )

    tipo_entrevista = forms.ChoiceField(
        choices=Cli057AsignacionEntrevista.TIPO_ENTREVISTA,
        label='Tipo de Entrevista',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_crear_entrevista'
        self.helper.form_class = 'w-200'

        self.helper.layout = Layout(
                Row(
                    Column('fecha_entrevista', css_class='form-group mb-0'),
                    Column('hora_entrevista', css_class='form-group mb-0'),
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