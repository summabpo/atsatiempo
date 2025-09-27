from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from crispy_forms.bootstrap import FormActions


class EmailForm(forms.Form):
    """
    Formulario para recibir email del usuario
    """
    email = forms.EmailField(
        label='Correo Electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu correo electrónico, el que tiene asociado tu cuenta',
            'autocomplete': 'email'
        })
    )
    
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_email_user'
        self.helper.form_class = 'needs-validation'
        self.helper.form_enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
            # Add the link in a new Div
            
            Submit('submit', 'Continuar', css_class='btn btn-lg btn-primary w-100 mb-5'),
            # Row(
            #     HTML('<div class="text-center mb-3"><a href="" class="link-primary fs-6 fw-bold">Forgot Password ?</a></div>'),
            #     css_class='fv-row mb-10'
            # ),
        )

class EmailUserForm(forms.Form):
    """
    Formulario para escribir una contraseña y confirmarla
    """
    password = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            
        })
    )
    confirm_password = forms.CharField(
        label='Confirmar Contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_email_user'
        self.helper.form_class = 'needs-validation'
        self.helper.form_enctype = 'multipart/form-data'

        self.helper.layout = Layout(
            Row(
                Column('password', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('confirm_password', css_class='form-group mb-0'),
                css_class='row'
            ),
            Submit('submit', 'Cambiar Contraseña', css_class='btn btn-lg btn-primary w-100 mb-5'),
        )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data
    
