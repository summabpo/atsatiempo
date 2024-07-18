import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from common.models import Cat001Estado, Cat004Ciudad
from ..models import Can101Candidato, Can102Experiencia, Can103Educacion, Can104Skill

class CandidatoForm(forms.Form):
    estado_id_001 = forms.ModelChoiceField(label='ESTADO', queryset=Cat001Estado.objects.all(), required=True)
    email = forms.CharField(label='EMAIL', required=True , widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    primer_nombre = forms.CharField(label='PRIMER NOMBRE', required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Primer Nombre'}))
    segundo_nombre = forms.CharField(label='SEGUNDO NOMBRE', required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Segundo Nombre'}))
    primer_apellido = forms.CharField(label='PRIMER APELLIDO', required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Primer Apellido'}))
    segundo_apellido = forms.CharField(label='SEGUNDO APELLIDO', required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Segundo Apellido'}))
    ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    sexo = forms.ChoiceField(label='GENERO', choices=[ ('', '---'), ('M', 'MASCULINO'), ('F', 'FEMENINO')], required=True)
    fecha_nacimiento = forms.DateField(label='FECHA NACIMIENTO',  required=True)
    telefono = forms.CharField(label='TELEFONO'    , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Teléfono'}))

    def __init__(self, *args, **kwargs):
        super(CandidatoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('primer_nombre', css_class='col-md-3'),
                Column('segundo_nombre', css_class='col-md-3'),
                Column('primer_apellido', css_class='col-md-3'),
                Column('segundo_apellido', css_class='col-md-3'),
            ),
            Row(
                Column('email', css_class='col-md-6'),
                Column('telefono', css_class='col-md-6'),
            ),
            Row(
                Column('fecha_nacimiento', css_class='js-flatpickr col-md-4'),
                Column('sexo', css_class='col-md-4'),
                Column('ciudad_id_004', css_class='col-md-4'),
                
            ),
            Row(
                Column('estado_id_001', css_class='col-md-12'),
            ),
            Submit('submit', 'Guardar')
        )

    def clean(self):
        cleaned_data = super().clean()
        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        email = cleaned_data.get('email')

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
