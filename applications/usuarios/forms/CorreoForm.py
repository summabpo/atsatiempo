from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML

class CorreoForm(forms.Form):
    email = forms.CharField(label='Correo', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese su correo'}), max_length=150)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_correo'
        self.helper.form_class = ''
        
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
            Submit('submit', 'Enviar Correo', css_class='btn btn-lg btn-primary w-100 mb-5'),
        )