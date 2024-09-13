import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML

class SignupFormCandidato(forms.Form):

    # Campos del usuario
    primer_nombre = forms.CharField(
        label='Nombre', 
        widget=forms.TextInput(attrs={'placeholder': 'Primer '}),
        max_length=150
    )
    
    segundo_nombre = forms.CharField(
        label='Nombre', 
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del usuario'}),
        max_length=150
    )
    
    primer_apellido = forms.CharField(
        label='Apellido', 
        widget=forms.TextInput(attrs={'placeholder': 'Apellido del usuario'}),
        max_length=150
    )

    segundo_apellido = forms.CharField(
        label='Apellido', 
        widget=forms.TextInput(attrs={'placeholder': 'Apellido del usuario'}),
        max_length=150
    )
    
    
    email = forms.EmailField(
        label='Correo electrónico Usuario', 
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'})
    )
    password1 = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'})
    )


    def clean(self):
        cleaned_data = super().clean()
        primer_nombre = cleaned_data.get('primer_nombre')
        segundo_nombre = cleaned_data.get('segundo_nombre')
        primer_apellido = cleaned_data.get('primer_apellido')
        segundo_apellido = cleaned_data.get('segundo_apellido')
        email = cleaned_data.get('email')
        


        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_nombre):
            self.add_error('primer_nombre', "Solo puede contener letras.")
        else:
            self.cleaned_data['primer_nombre'] = primer_nombre.upper()
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_nombre):
            self.add_error('segundo_nombre', "Solo puede contener letras.")
        else:
            self.cleaned_data['segundo_nombre'] = segundo_nombre.upper()
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', primer_apellido):
            self.add_error('primer_apellido', "Solo puede contener letras.")
        else:
            self.cleaned_data['primer_apellido'] = primer_apellido.upper()
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', segundo_apellido):
            self.add_error('segundo_apellido', "Solo puede contener letras.")
        else:
            self.cleaned_data['segundo_apellido'] = segundo_apellido.upper()

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email','El Correo no es válido.')