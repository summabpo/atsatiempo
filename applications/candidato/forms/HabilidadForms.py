import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden, Div, Submit, HTML
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato, Can104Skill, Can101CandidatoSkill
from applications.services.choices import NIVEL_HABILIDAD_CHOICES_STATIC


level_Choices = [
    ('', '---------------'),
    (1, 'Básico'),
    (2, 'Intermedio'),
    (3, 'Superior')
    # Agrega más opciones según sea necesario
]

class HabilidadCandidatoForm(forms.Form):
    ability = forms.CharField(label='Habilidad')
    level =  forms.ChoiceField(choices=level_Choices, label='Nivel', widget = forms.Select(attrs={ 'class': 'form-select form-select-solid fw-bold'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Actualizar choices dinámicamente
        self.fields['ability'].widget.attrs.update({
            'class': 'form-control form-control-solid', 
            'id': 'habilidad', 
            'required': 'required'
            
        })

        self.fields['level'] = forms.ChoiceField(
            label='Nivel',
            choices=level_Choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',  # Clases CSS del campo  
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccion una opción',
                    }
        ), required=True)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_habilidades'
        self.helper.layout = Layout(
            Row(
                    Column('ability', css_class='form-group col-md-12 mb-0'),
            ),
            Row(
                    HTML('<div id="sugerencias" class="d-flex flex-column"></div>'),
            ),
            Row(
                    Column('level', css_class='form-group col-md-12 mb-0'),
            ),
        )



    def clean(self):
        cleaned_data = super().clean()
        ability = cleaned_data.get('ability')
        level = cleaned_data.get('level')

        return cleaned_data

class CandidateHabilityForm(forms.Form):
    skill_id_104 = forms.CharField(
        label='Habilidad',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Escriba una habilidad',
        })
    )
    nivel = forms.ChoiceField(
        choices=NIVEL_HABILIDAD_CHOICES_STATIC,
        label='Nivel',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            
        })
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_skill'
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Habilidades</h4>"),
                    Div('skill_id_104', css_class='col-6'),
                    Div('nivel', css_class='col-6'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),  
        )

    def clean(self):
        cleaned_data = super().clean()
        skill_id_104 = cleaned_data.get('skill_id_104')
        nivel = cleaned_data.get('nivel')

        if not skill_id_104:
            self.add_error('skill_id_104', "Este campo es obligatorio.")
        if not nivel:
            self.add_error('nivel', "Este campo es obligatorio.")

        return cleaned_data

