from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from applications.usuarios.models import Grupo, UsuarioBase

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    model = UsuarioBase

