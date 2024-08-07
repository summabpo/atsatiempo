import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden, Div, Submit
from applications.common.models import Cat001Estado
from applications.candidato.models import Can101Candidato, Can102Experiencia

class ExperienciaCandidatoForm(forms.Form):
    estado_id_001 = forms.ModelChoiceField(label='ESTADO', queryset=Cat001Estado.objects.all(), required=False)
    entidad = forms.CharField(label='ENTIDAD', required=True , widget=forms.TextInput(attrs={'placeholder': 'Entidad o Nombre Empresa'}))
    sector = forms.CharField(label='SECTOR', required=True , widget=forms.TextInput(attrs={'placeholder': 'Sector'}))
    fecha_inicial = forms.DateField(label='FECHA DE INICIO', widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    fecha_final = forms.DateField(label='FECHA TERMINACION', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    activo = forms.ChoiceField(label='ACTIVO', choices=[ ('', '---'), ('SI', 'SI'), ('NO', 'NO')], required=True)
    logro = forms.CharField(label='LOGROS', required=True, widget=forms.Textarea(attrs={'placeholder': 'Descripción de la Empresa'}))
    cargo = forms.CharField(label='CARGO',  required=True, widget=forms.TextInput(attrs={'placeholder': 'Cargo Desempeñado'}))

    def __init__(self, *args, **kwargs):
        self.candidato_id = kwargs.pop('candidato_id', None)
        super(ExperienciaCandidatoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        self.helper.layout = Layout(
            Div(
                Div('entidad', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('sector', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('activo', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('fecha_inicial', css_class='col'),
                Div('fecha_final', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('cargo', css_class='col form-group'),
                css_class='row'
            ),
            Div(
                Div('logro', css_class='col form-group'),
                css_class='row'
            ),
            # Div(
            #     Div('estado_id_001', css_class='col form-group'),
            #     css_class='row'
            # ),
            Submit('submit_experiencia', 'Guardar Experiencia', css_class='btn btn-primary mt-3'),
        )
    
    def clean(self):
        cleaned_data = super().clean()

        entidad = cleaned_data.get('entidad')
        sector = cleaned_data.get('sector')
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        activo = cleaned_data.get('activo')
        logro = cleaned_data.get('logro')
        cargo = cleaned_data.get('logro')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', entidad):
            self.add_error('entidad', "La entidad solo puede contener letras.")
        else:
            self.cleaned_data['entidad'] = entidad.upper()

        self.cleaned_data['cargo'] = entidad.upper()
            

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', sector):
            self.add_error('sector', "La entidad solo puede contener letras.")
        else:
            self.cleaned_data['sector'] = sector.upper()

        fecha_actual = timezone.now().date()

        if fecha_actual > fecha_inicial:
            if activo == 'SI':
                if fecha_final is None or fecha_final == '':
                    self.add_error('fecha_final', "La fecha final no puede ir vacia si termino el trabajo")
        else:
            self.add_error('fecha_inicial', "La fecha actual es menor que la fecha inicial")
        
        if len(logro.split()) < 15:
            self.add_error('logro','La descripción debe contener al menos 30 palabras')

        

        return cleaned_data

    def save(self, candidato_id):
        estado_id_001 = Cat001Estado.objects.get(id=1)
        entidad       = self.cleaned_data['entidad']
        sector        = self.cleaned_data['sector']
        fecha_inicial = self.cleaned_data['fecha_inicial']
        fecha_final   = self.cleaned_data['fecha_final']
        activo        = self.cleaned_data['activo']
        logro         = self.cleaned_data['logro']
        cargo         = self.cleaned_data['cargo']
        candidato_id_101 = Can101Candidato.objects.get(id=candidato_id)

        experiencia = Can102Experiencia(
            estado_id_001 = estado_id_001,
            entidad = entidad,
            sector = sector,
            fecha_inicial = fecha_inicial,
            fecha_final = fecha_final,
            activo = activo,
            logro = logro,
            candidato_id_101= candidato_id_101,
            cargo = cargo,
        )

        experiencia.save()