import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden, Div, Submit
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato, Can103Educacion

class EstudioCandidatoForm(forms.Form):
    estado_id_001 = forms.ModelChoiceField(label='ESTADO', queryset=Cat001Estado.objects.all(), required=False)
    institucion = forms.CharField(label='INSTITUCION', required=True , widget=forms.TextInput(attrs={'placeholder': 'Institución'}))
    fecha_inicial = forms.DateField(label='FECHA DE INICIO', widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    fecha_final = forms.DateField(label='FECHA TERMINACION', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    # grado_en = forms.CharField(label='GRADO EN', required=False , widget=forms.TextInput(attrs={'placeholder': 'Grado en'}))
    grado_en = forms.BooleanField(
        label='¿GRADUADO?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Marque si tiene un grado'
    )
    titulo = forms.CharField(label='TITULO', required=True , widget=forms.TextInput(attrs={'placeholder': 'Titulo'}))
    carrera = forms.CharField(label='CARRERA', required=True , widget=forms.TextInput(attrs={'placeholder': 'Carrera'}))
    fortaleza_adquiridas = forms.CharField(label='LOGROS', required=True, widget=forms.Textarea(attrs={'placeholder': 'Descripción de la Fortalezas'}))
    ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    
    def __init__(self, *args, **kwargs):
        self.candidato_id = kwargs.pop('candidato_id', None)
        super(EstudioCandidatoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.form_class = 'container'
        self.helper.layout = Layout(
            Div(
                Div('institucion', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('grado_en', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('fecha_inicial', css_class='col'),
                Div('fecha_final', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('titulo', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('carrera', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('fortaleza_adquiridas', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('ciudad_id_004', css_class='col'),
                css_class='row'
            ),
            # Div(
            #     Div('estado_id_001', css_class='col'),
            #     css_class='row'
            # ),
            Submit('submit_estudio', 'Guardar Estudio', css_class='btn btn-primary mt-3'),
        )  
    
    def clean(self):
        cleaned_data =  super().clean()

        institucion = cleaned_data.get('institucion')
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        grado_en = cleaned_data.get('grado_en')
        titulo = cleaned_data.get('titulo')
        carrera = cleaned_data.get('carrera')
        fortaleza_adquiridas = cleaned_data.get('fortaleza_adquiridas')
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', institucion):
            self.add_error('institucion', "La Instirución solo puede contener letras.")
        else:
            self.cleaned_data['institucion'] = institucion.upper()

        fecha_actual = timezone.now().date()


        if fecha_actual > fecha_inicial:
            if grado_en:
                if fecha_final is None or fecha_final == '':
                    self.add_error('fecha_final', "La fecha final no puede ir vacia si termino los estudios")
            
        else:
            self.add_error('fecha_inicial', "La fecha actual es mayot que la fecha inicial")

        # if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', grado_en):
        #     self.add_error('grado_en', "La Instirución solo puede contener letras.")
        # else:
        #     self.cleaned_data['grado_en'] = grado_en.upper()
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', titulo):
            self.add_error('titulo', "La Instirución solo puede contener letras.")
        else:
            self.cleaned_data['titulo'] = titulo.upper()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', carrera):
            self.add_error('carrera', "La Instirución solo puede contener letras.")
        else:
            self.cleaned_data['carrera'] = carrera.upper()

        if len(fortaleza_adquiridas.split()) < 10:
            self.add_error('fortaleza_adquiridas','La descripción debe contener al menos 10 palabras')

        return cleaned_data

    def save(self, candidato_id):

        if not self.is_valid():
            raise ValueError("El formulario no es válido")
    
        estado_id_001 = Cat001Estado.objects.get(id=1)
        institucion   = self.cleaned_data['institucion'] 
        fecha_inicial = self.cleaned_data['fecha_inicial']
        fecha_final   = self.cleaned_data['fecha_final']
        grado_en      = self.cleaned_data['grado_en']
        titulo        = self.cleaned_data['titulo']
        carrera       = self.cleaned_data['carrera']
        fortaleza_adquiridas = self.cleaned_data['fortaleza_adquiridas']
        ciudad_id_004 = self.cleaned_data['ciudad_id_004']
        candidato_id_101 = Can101Candidato.objects.get(id=candidato_id)
        
        estudio = Can103Educacion(
            estado_id_001 = estado_id_001,
            institucion = institucion,
            fecha_inicial = fecha_inicial,
            fecha_final = fecha_final,
            grado_en = grado_en,
            titulo = titulo,
            carrera= carrera,
            fortaleza_adquiridas= fortaleza_adquiridas,
            ciudad_id_004= ciudad_id_004,
            candidato_id_101= candidato_id_101,
        )

        estudio.save()