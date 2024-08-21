import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden, Div, Submit
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato, Can104Skill, Can101CandidatoSkill

class HabilidadCandidatoForm(forms.Form):
    candidato_id_101 = forms.ModelChoiceField(label='CANDIDATO', queryset=Can101Candidato.objects.all(), required=False)
    skill_id_104 = forms.ModelChoiceField(label='HABILIDAD', queryset=Can104Skill.objects.all(), required=True)
    nivel = forms.ChoiceField(label='NIVEL', choices=[ ('', '---'), ('1', 'BÁSICO'), ('2', 'INTERMEDIO'), ('3', 'SUPERIOR')], required=True)

    def __init__(self, *args, **kwargs):
        self.candidato_id = kwargs.pop('candidato_id', None)
        super(HabilidadCandidatoForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.fields['skill_id_104'].widget.attrs.update({
            'data-placeholder': 'Select a Country...',
            'class': 'select2-selection select2-selection--multiple'
        })

        self.helper.layout = Layout(
            Row(
                Column('skill_id_104', css_class='form-group mb-0'),
                Column('nivel', css_class='form-group mb-0 select2'),
                Submit('submit_habilidad', 'Crear', css_class='btn btn-light-info mb-0'),
                css_class='row'
            ),
        )

    def clean(self):
        cleaned_data =  super().clean()

        candidato_id_101 = cleaned_data.get('candidato_id_101')
        skill_id_104 = cleaned_data.get('skill_id_104')
        nivel = cleaned_data.get('nivel')

        return cleaned_data
    
    def save(self, candidato_id):
        candidato_id_101 = Can101Candidato.objects.get(id=candidato_id)
        skill_id_104 = self.cleaned_data.get('skill_id_104')
        nivel = self.cleaned_data.get('nivel')

        hablidad = Can101CandidatoSkill(
            candidato_id_101 = candidato_id_101,
            skill_id_104 = skill_id_104,
            nivel = nivel,
        )

        hablidad.save()