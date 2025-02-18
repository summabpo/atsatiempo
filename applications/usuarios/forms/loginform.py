from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML

class LoginForm(forms.Form):
    username = forms.CharField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}), max_length=150)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_login'
        self.helper.form_class = ''
        
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
            Row(
                Column('password', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
            # Add the link in a new Div
            
            Submit('submit', 'Continuar', css_class='btn btn-lg btn-primary w-100 mb-5'),
            # Row(
            #     HTML('<div class="text-center mb-3"><a href="" class="link-primary fs-6 fw-bold">Forgot Password ?</a></div>'),
            #     css_class='fv-row mb-10'
            # ),
        )
