import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden, Div, Submit
from applications.candidato.models import  Can101CandidatoSkill , Can104Skill


level_Choices = [
    ('', '---------------'),
    (1, 'Básico'),
    (2, 'Intermedio'),
    (3, 'Superior')
    # Agrega más opciones según sea necesario
]

class PruebasForm(forms.Form):
    ability = forms.ChoiceField(choices=[], label='Habilidad')
    level =  forms.ChoiceField(choices=level_Choices, label='Nivel' ,widget=forms.Select(attrs={'data-control': 'select2'}))
    
    def __init__(self, *args, **kwargs):
        super(PruebasForm, self).__init__(*args, **kwargs)

        # Actualizar choices dinámicamente
        self.fields['ability'].choices = [('', '----------')] + [(item.estado_id_004, item.nombre) for item in Can104Skill.objects.all().order_by('nombre')]

        

        self.helper = FormHelper()
        self.helper.form_id = 'form_habilidades'
        self.helper.layout = Layout(
            Row(
                Column('ability', css_class='form-group mb-0'),
                Column('level', css_class='form-group mb-0'),
                Submit('submit', 'Filtrar', css_class='btn btn-light-info mb-0'),
                css_class='row'
            ),
            
            
            
        )
    
    