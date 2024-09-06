from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML


class groupsForm(forms.Form):
    name = forms.CharField(label='Nombre', widget=forms.TextInput(attrs={'placeholder': 'Nombre del Grupo '}), max_length=150)
    descripcion  = forms.CharField(
        label='descripcion',
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'descripcion de grupo',
                'rows': 5,  
                'cols': 40,  
                'class': 'fixed-size-textarea'
            }
        )
    )
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_groups'
        self.helper.form_class = ''
        
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
            Row(
                Column('descripcion', css_class='form-group mb-0'),
                css_class='fv-row mb-10'
            ),
        )
