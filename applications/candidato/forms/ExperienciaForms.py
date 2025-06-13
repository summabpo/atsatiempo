import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden, Div, Submit, HTML
from applications.common.models import Cat001Estado
from applications.candidato.models import Can101Candidato, Can102Experiencia
from applications.services.choices import MODALIDAD_CHOICES_STATIC, MOTIVO_SALIDA_CHOICES_STATIC

class ExperienciaCandidatoForm(forms.Form):
    estado_id_001 = forms.ModelChoiceField(label='ESTADO', queryset=Cat001Estado.objects.all(), required=False)
    entidad = forms.CharField(label='ENTIDAD', required=True , widget=forms.TextInput(attrs={'placeholder': 'Entidad o Nombre Empresa'}))
    sector = forms.CharField(label='SECTOR', required=True , widget=forms.TextInput(attrs={'placeholder': 'Sector'}))
    fecha_inicial = forms.DateField(label='FECHA DE INICIO', widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    fecha_final = forms.DateField(label='FECHA TERMINACION', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    activo =  forms.BooleanField(
        label='ACTIVO',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    
    
    cargo = forms.CharField(label='CARGO',  required=True, widget=forms.TextInput(attrs={'placeholder': 'Cargo Desempeñado'}))
    
    logro = forms.CharField(
        label='LOGROS',
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Tus logros empresariales',
                'rows': 5,  
                'cols': 40,  
                'class': 'fixed-size-textarea'
            }
        )
    )
    

    def __init__(self, *args, **kwargs):
        self.candidato_id = kwargs.pop('candidato_id', None)
        super(ExperienciaCandidatoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_experienciacandidato'
        self.helper.form_class = 'container'
        
        self.helper.layout = Layout(
            Div(
                Div('entidad', css_class='col'),
                Div('sector', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('activo', css_class='col'),
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
        )
    
    def clean(self):
        cleaned_data = super().clean()

        entidad = cleaned_data.get('entidad')
        sector = cleaned_data.get('sector')
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        activo = cleaned_data.get('activo')
        logro = cleaned_data.get('logro')
        cargo = cleaned_data.get('cargo')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', entidad):
            self.add_error('entidad', "La entidad solo puede contener letras.")
        else:
            self.cleaned_data['entidad'] = entidad.upper()

        self.cleaned_data['cargo'] = cargo.upper()
            

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
        
        if len(logro.split()) < 10:
            self.add_error('logro','La descripción debe contener al menos 10 palabras')

        

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


class candidateJobForm(forms.Form):
    entidad = forms.CharField(
        label='Entidad',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Entidad o Nombre Empresa'})
    )

    sector = forms.CharField(
        label='Sector',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Sector'})
    )

    fecha_inicial = forms.DateField(
        label='Fecha Inicial',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    fecha_final = forms.DateField(
        label='Fecha Final',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    activo = forms.BooleanField(
        label='Activo',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    logro = forms.CharField(
        label='Logro',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe tus logros',
            'rows': 5,
            'cols': 40
        })
    )

    cargo = forms.CharField(
        label='Cargo',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Cargo Desempeñado'})
    )

    motivo_salida = forms.ChoiceField(
        label='Motivo de Salida',
        choices=MOTIVO_SALIDA_CHOICES_STATIC,
        required=False,
        # Define los atributos comunes aquí.
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-control': 'select2',
        })
    )

    salario = forms.DecimalField(
        label='Salario',
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Salario'})
    )

    modalidad_trabajo = forms.ChoiceField(
        label='Modalidad de Trabajo',
        choices=MODALIDAD_CHOICES_STATIC,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-control': 'select2',
        })
    )

    nombre_jefe = forms.CharField(
        label='Nombre del Jefe',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del jefe directo'})
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_trabajo'

        if not self.instance:
            self.fields['motivo_salida'].widget.attrs['data-dropdown-parent'] = '#trabajos_candidato'
            self.fields['modalidad_trabajo'].widget.attrs['data-dropdown-parent'] = '#trabajos_candidato'
            

        self.helper.layout = Layout(
            Div(
            Div(
                HTML("<h4 class='mb-3 text-primary'>Información Laboral</h4>"),
                Div('entidad', css_class='col-12'),
                Div('sector', css_class='col-12'),
                Div('cargo', css_class='col-12'),
                Div('activo', css_class='col-12'),
                Div('fecha_inicial', css_class='col-6'),
                Div('fecha_final', css_class='col-6 campo-activo'),
                Div('motivo_salida', css_class='col-12 campo-activo'),
                Div('salario', css_class='col-6 campo-activo'),
                Div('modalidad_trabajo', css_class='col-6 campo-activo'),
                Div('nombre_jefe', css_class='col-12 campo-activo'),
                Div('logro', css_class='col-12'),
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        entidad = cleaned_data.get('entidad')
        sector = cleaned_data.get('sector')
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        activo = cleaned_data.get('activo')
        logro = cleaned_data.get('logro')
        cargo = cleaned_data.get('cargo')
        motivo_salida = cleaned_data.get('motivo_salida')
        
        if motivo_salida == '':
            cleaned_data['motivo_salida'] = None


        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', entidad):
            self.add_error('entidad', "La entidad solo puede contener letras.")
        else:
            self.cleaned_data['entidad'] = entidad.upper()
            
        self.cleaned_data['cargo'] = cargo.upper()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', sector):
            self.add_error('sector', "La entidad solo puede contener letras.")
        else:
            self.cleaned_data['sector'] = sector.upper()

        if fecha_inicial and fecha_final and fecha_final < fecha_inicial:
            self.add_error('fecha_final', "La fecha final no puede ser menor que la fecha inicial.")
        fecha_actual = timezone.now().date()

        if activo:
            if fecha_final:
                self.add_error('fecha_final', "No debe proporcionar una fecha final si el trabajo está activo.")
        elif not fecha_final:
            self.add_error('fecha_final', "La fecha final no puede ir vacía si el trabajo no está activo.")
        elif fecha_final < fecha_inicial:
            self.add_error('fecha_final', "La fecha final no puede ser menor que la fecha inicial.")
        elif fecha_inicial and fecha_inicial > fecha_actual:
            self.add_error('fecha_inicial', "La fecha inicial no puede ser mayor que la fecha actual.")

        if logro:
            if len(logro.split()) > 500:
                self.add_error('logro','La descripción debe contener máximo 500 palabras')

        return cleaned_data
        