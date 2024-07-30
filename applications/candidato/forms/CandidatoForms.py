import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Layout, Div, Submit, HTML
from applications.common.models import Cat001Estado, Cat004Ciudad
from ..models import Can101Candidato

class CandidatoForm(forms.Form):
    estado_id_001 = forms.ModelChoiceField(label='ESTADO', queryset=Cat001Estado.objects.all(), required=True)
    email = forms.CharField(label='EMAIL', required=True , widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    primer_nombre = forms.CharField(label='PRIMER NOMBRE', required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Primer Nombre'}))
    segundo_nombre = forms.CharField(label='SEGUNDO NOMBRE', required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Segundo Nombre'}))
    primer_apellido = forms.CharField(label='PRIMER APELLIDO', required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Primer Apellido'}))
    segundo_apellido = forms.CharField(label='SEGUNDO APELLIDO', required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Segundo Apellido'}))
    ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    sexo = forms.ChoiceField(label='GENERO', choices=[ ('', '---'), ('M', 'MASCULINO'), ('F', 'FEMENINO')], required=True)
    fecha_nacimiento = forms.DateField(label='FECHA DE NACIMIENTO', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    telefono = forms.CharField(label='TELEFONO'    , required=True , widget=forms.TextInput(attrs={'placeholder': 'Teléfono'}))

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(CandidatoForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['estado_id_001'].initial = self.instance.estado_id_001
            self.fields['email'].initial = self.instance.email
            self.fields['primer_nombre'].initial = self.instance.primer_nombre
            self.fields['segundo_nombre'].initial = self.instance.segundo_nombre
            self.fields['primer_apellido'].initial = self.instance.primer_apellido
            self.fields['segundo_apellido'].initial = self.instance.segundo_apellido
            self.fields['ciudad_id_004'].initial = self.instance.ciudad_id_004
            self.fields['sexo'].initial = self.instance.sexo
            self.fields['fecha_nacimiento'].initial = self.instance.fecha_nacimiento
            self.fields['telefono'].initial = self.instance.telefono

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # self.helper.layout = Layout(
        #     Row(
        #         Column('primer_nombre'),
        #         Column('segundo_nombre'),
        #         Column('primer_apellido'),
        #         Column('segundo_apellido'),
        #     ),
        #     Row(
        #         Column('email'),
        #         Column('telefono'),
        #     ),
        #     Row(
        #         Column('fecha_nacimiento', css_class='col-md-4'),
        #         Column('sexo', css_class='col-md-4'),
        #         Column('ciudad_id_004', css_class='col-md-4'),
                
        #     ),
        #     Row(
        #         Column('estado_id_001', css_class='col-md-12'),
        #     ),
        #     Submit('submit', 'Guardar')
        # )

        self.helper.form_class = 'container'
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('primer_nombre', css_class='col'),
                    Div('segundo_nombre', css_class='col'),
                    Div('primer_apellido', css_class='col'),
                    Div('segundo_apellido', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('email', css_class='col'),
                    Div('telefono', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('fecha_nacimiento', css_class='col'),
                    Div('sexo', css_class='col'),
                    Div('ciudad_id_004', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('estado_id_001', css_class='col'),
                    css_class='row'
                ),
                Submit('submit_candidato', 'Guardar Empleado', css_class='btn btn-primary mt-3'),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        email = cleaned_data.get('email')
        telefono = cleaned_data.get('telefono')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_nombre):
            self.add_error('primer_nombre', "El campo solo puede contener letras.")
        else:
            self.cleaned_data['primer_nombre'] = primer_nombre.upper()     

        if segundo_nombre:  # Verifica si el campo no está vacío
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_nombre):
                self.add_error('segundo_nombre', "El segundo nombre solo puede contener letras.")
            else:
                self.cleaned_data['segundo_nombre'] = segundo_nombre.upper()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_apellido):
            self.add_error('primer_apellido', "El campo solo puede contener letras.")
        else:
            self.cleaned_data['primer_apellido'] = primer_apellido.upper()   

        if segundo_apellido:  # Verifica si el campo no está vacío
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_apellido):
                # self.add_error("El campo solo puede contener letras.")
                self.add_error('segundo_apellido', "El segundo apellido solo puede contener letras.")
            else:
                self.cleaned_data['segundo_apellido'] = segundo_apellido.upper()  

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email','El email no es válido.')

        if not re.match(r'^\d{10}$', telefono):
            self.add_error('telefono','El teléfono debe contener solo números y tener 10 dígitos.')
        
        return cleaned_data

    def save(self):
        if self.instance:
            candidato = self.instance
        else:
            candidato = Can101Candidato()
        
        candidato.estado_id_001 = self.cleaned_data['estado_id_001']
        candidato.email = self.cleaned_data['email']
        candidato.primer_nombre = self.cleaned_data['primer_nombre']
        candidato.segundo_nombre = self.cleaned_data['segundo_nombre']
        candidato.primer_apellido = self.cleaned_data['primer_apellido']
        candidato.segundo_apellido = self.cleaned_data['segundo_apellido']
        candidato.telefono = self.cleaned_data['telefono']
        candidato.ciudad_id_004 = self.cleaned_data['ciudad_id_004']
        candidato.sexo = self.cleaned_data['sexo']
        candidato.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']


        candidato.save()