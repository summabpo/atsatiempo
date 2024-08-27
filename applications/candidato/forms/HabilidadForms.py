import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden, Div, Submit
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato, Can104Skill, Can101CandidatoSkill

level_Choices = [
    ('', '---------------'),
    (1, 'Básico'),
    (2, 'Intermedio'),
    (3, 'Superior')
    # Agrega más opciones según sea necesario
]

class HabilidadCandidatoForm(forms.Form):
    ability = forms.ChoiceField(choices=[], label='Habilidad',widget=forms.Select(attrs={'data-control': 'select2' ,' data-dropdown-parent':'#kt_modal_1','data-tags':'true'}) )
    level =  forms.ChoiceField(choices=level_Choices, label='Nivel',widget=forms.Select(attrs={ 'class': 'form-select form-select-solid fw-bold'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Actualizar choices dinámicamente
        self.fields['ability'].choices = [('', '----------')] + [(item.id, item.nombre) for item in Can104Skill.objects.all().order_by('nombre')]

        self.fields['ability'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags':'true',
            'data-dropdown-parent': '#kt_modal_1',
            'class': 'form-select form-select-solid fw-bold',
            
        })
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_habilidades'
        self.helper.layout = Layout(
            Div(
                
                Div('ability',css_class='me-4 mb-0'),
                Div('level',css_class='me-4 mb-0'),
                Submit('submit', 'Agregar', css_class='btn btn-lg btn-primary px-8'),
                css_class='d-flex align-items-center'), 
    

        )

    