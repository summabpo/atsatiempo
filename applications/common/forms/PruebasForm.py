from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Div, Submit
from applications.candidato.models import Can101CandidatoSkill

level_Choices = [
    ('', '---------------'),
    (1, 'Básico'),
    (2, 'Intermedio'),
    (3, 'Superior')
    # Agrega más opciones según sea necesario
]

class HabilidadForm(forms.Form):
    habilidad = forms.CharField(label='Habilidad', required=True)
    nivel = forms.ChoiceField(choices=level_Choices, label='Nivel', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'habilidadesForm'
        self.helper.form_method = 'post'
        
        self.fields['habilidad'].widget.attrs.update({'class': 'form-control', 'id': 'habilidad', 'required': 'required'})
        self.fields['nivel'].widget.attrs.update({'class': 'form-control', 'id': 'nivel', 'required': 'required'})

        self.helper.layout = Layout(
            Div(
                Div('habilidad',css_class='me-4 mb-0'),
                Div('nivel',css_class='me-4 mb-0'),
                Submit('submit', 'Agregar', css_class='btn btn-lg btn-primary px-8'),
                css_class='d-flex align-items-center'), 
        )