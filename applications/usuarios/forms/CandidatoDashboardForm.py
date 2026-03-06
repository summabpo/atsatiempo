"""
Formulario de información del candidato para el dashboard admin.
"""
from django import forms
from applications.common.models import Cat004Ciudad
from applications.services.choices import GENERO_CHOICES_STATIC


class CandidatoDashboardForm(forms.Form):
    """Formulario completo de información del candidato para el dashboard admin."""
    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Correo'})
    )
    primer_nombre = forms.CharField(
        label='Primer nombre',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Primer nombre'})
    )
    segundo_nombre = forms.CharField(
        label='Segundo nombre',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Segundo nombre'})
    )
    primer_apellido = forms.CharField(
        label='Primer apellido',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Primer apellido'})
    )
    segundo_apellido = forms.CharField(
        label='Segundo apellido',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Segundo apellido'})
    )
    numero_documento = forms.CharField(
        label='Número de documento',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Documento'})
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Teléfono'})
    )
    ciudad_id_004 = forms.ModelChoiceField(
        label='Ciudad',
        queryset=Cat004Ciudad.objects.all().order_by('nombre'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-solid'})
    )
    sexo = forms.ChoiceField(
        label='Género',
        choices=GENERO_CHOICES_STATIC,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-solid'})
    )
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-solid'})
    )
    direccion = forms.CharField(
        label='Dirección',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Dirección'})
    )
    aspiracion_salarial = forms.IntegerField(
        label='Aspiración salarial',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-solid', 'placeholder': '0', 'min': '0'})
    )
    perfil = forms.CharField(
        label='Perfil profesional',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 4, 'placeholder': 'Descripción del perfil'})
    )
    imagen_perfil = forms.ImageField(
        label='Imagen de perfil',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control form-control-solid', 'accept': 'image/*'})
    )
    hoja_de_vida = forms.FileField(
        label='Hoja de vida',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control form-control-solid', 'accept': '.pdf,.doc,.docx'})
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['email'].initial = self.instance.email
            self.fields['primer_nombre'].initial = self.instance.primer_nombre
            self.fields['segundo_nombre'].initial = self.instance.segundo_nombre
            self.fields['primer_apellido'].initial = self.instance.primer_apellido
            self.fields['segundo_apellido'].initial = self.instance.segundo_apellido
            self.fields['numero_documento'].initial = self.instance.numero_documento
            self.fields['telefono'].initial = self.instance.telefono
            self.fields['ciudad_id_004'].initial = self.instance.ciudad_id_004
            self.fields['sexo'].initial = self.instance.sexo
            self.fields['fecha_nacimiento'].initial = self.instance.fecha_nacimiento
            self.fields['direccion'].initial = self.instance.direccion
            self.fields['aspiracion_salarial'].initial = self.instance.aspiracion_salarial
            self.fields['perfil'].initial = self.instance.perfil
            self.fields['imagen_perfil'].initial = self.instance.imagen_perfil
            self.fields['hoja_de_vida'].initial = self.instance.hoja_de_vida

    def save(self):
        if not self.instance:
            raise ValueError('Se requiere una instancia de candidato para guardar.')
        candidato = self.instance
        candidato.email = self.cleaned_data['email']
        candidato.primer_nombre = self.cleaned_data['primer_nombre']
        candidato.segundo_nombre = self.cleaned_data['segundo_nombre'] or None
        candidato.primer_apellido = self.cleaned_data['primer_apellido']
        candidato.segundo_apellido = self.cleaned_data['segundo_apellido'] or None
        candidato.numero_documento = self.cleaned_data['numero_documento'] or None
        candidato.telefono = self.cleaned_data['telefono'] or None
        candidato.ciudad_id_004 = self.cleaned_data['ciudad_id_004']
        candidato.sexo = self.cleaned_data['sexo'] or None
        candidato.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        candidato.direccion = self.cleaned_data['direccion'] or None
        candidato.aspiracion_salarial = self.cleaned_data['aspiracion_salarial']
        candidato.perfil = self.cleaned_data['perfil'] or None
        if self.cleaned_data.get('imagen_perfil'):
            candidato.imagen_perfil = self.cleaned_data['imagen_perfil']
        if self.cleaned_data.get('hoja_de_vida'):
            candidato.hoja_de_vida = self.cleaned_data['hoja_de_vida']
        candidato.save()
        return candidato
