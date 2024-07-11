
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from common.models import Cat004Ciudad


class ClienteForm(forms.Form):
    nit           = forms.CharField(label='NIT' , required=True  ,widget=forms.TextInput(attrs={'placeholder': 'Por favor ingrese NIT'}))
    razon_social  = forms.CharField(label='RAZON SOCIAL', required=True ,widget=forms.TextInput(attrs={'placeholder': 'Razón Social'}))
    ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    email         = forms.CharField(label='EMAIL'    , required=False ,widget=forms.TextInput(attrs={'placeholder': 'Sufijo costo'}))
    contacto      = forms.CharField(label='CONTACTO'    , required=False ,widget=forms.TextInput(attrs={'placeholder': 'Sufijo costo'}))
    telefono      = forms.CharField(label='TELEFONO'    , required=False ,widget=forms.TextInput(attrs={'placeholder': 'Sufijo costo'}))

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('nit'),
            Field('razon_social'),
            Field('ciudad_id_004', css_class='js-select2'),
            Field('email'),
            Field('contacto'),
            Field('telefono'),
            Submit('submit', 'Guardar', css_class='btn-primary')
        )