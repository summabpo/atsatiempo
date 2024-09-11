import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from applications.common.models import Cat004Ciudad, Cat001Estado

class SignupForm(forms.Form):
    # Campos del usuario
    name = forms.CharField(
        label='Nombre', 
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del usuario'}),
        max_length=150
    )
    
    last_name = forms.CharField(
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
    
    # Campos de la compañía
    nit = forms.IntegerField(
        label='NIT',
        widget=forms.NumberInput(attrs={'placeholder': 'Número de identificación tributaria'}),
        min_value=0,  # Asegura que el número sea positivo
    )
    companyname = forms.CharField(
        label='Nombre de la compañía', 
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de la compañía'}),
        max_length=150
    ) 
    
    companycontact = forms.CharField(
        label='Contacto de la compañía', 
        widget=forms.TextInput(attrs={'placeholder': 'Persona de compañía'}),
        max_length=150
    )
    companyemail = forms.EmailField(
        label='Correo electrónico de la compañía', 
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico de la compañía'}),
        max_length=150
    )

    
    
    
    def clean(self):
        cleaned_data = super().clean()
        nit = cleaned_data.get('nit')
        companyname = cleaned_data.get('companyname')
        companycontact = cleaned_data.get('companycontact')
        companyemail = cleaned_data.get('companyemail')
        
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', companyname):
            self.add_error('companyname', "El nombre solo puede contener letras.")
        else:
            self.cleaned_data['companyname'] = companyname.upper()
        
        if nit is not None:
            if not (100000000 <= nit <= 999999999):  # Verificar que el NIT tenga 9 dígitos
                self.add_error('nit', 'El NIT debe contener exactamente 9 dígitos.')


        if companyemail and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', companyemail):
            self.add_error('companyemail','El mail no es válido.')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', companycontact):
            self.add_error('companycontact','El Nombre del Contacto solo puede contener letras.')
        else:
            self.cleaned_data['companycontact'] = companycontact.upper()



        return super().clean()
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_signup'
        self.helper.form_class = 'w-200'
        
        
        cities = Cat004Ciudad.objects.all().order_by('nombre')
        city_choices = [('', '----------')] + [(ciudad.id, f"{ciudad.nombre}") for ciudad in cities]

        # Añadir el campo city al formulario con las opciones obtenidas
        self.fields['city'] = forms.ChoiceField(
            choices=city_choices,
            label='Ciudad',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select',
            })
        )
        
        
        # Definimos el layout del formulario
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group mb-0'),
                Column('last_name', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('email', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('password1', css_class='form-group mb-0'),
                Column('password2', css_class='form-group mb-0'),
                css_class='row'
            ),
            HTML('<div class="separator my-10"></div>'),
            Row(
                Column('nit', css_class='form-group mb-0'),
                Column('companyname', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
            Row(
                Column('city', css_class='form-group mb-0'),
                Column('companycontact', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
            Row(
                Column('companyemail', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
            Submit('submit', 'Crear', css_class='btn btn-lg btn-primary w-100 mb-5'),
            
        )
