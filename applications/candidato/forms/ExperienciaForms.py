import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden
from applications.common.models import Cat001Estado
from applications.candidato.models import Can101Candidato, Can102Experiencia

class ExperienciaCandidatoForm(forms.Form):
    estado_id_001 = forms.ModelChoiceField(label='ESTADO', queryset=Cat001Estado.objects.all(), required=True)
    entidad = forms.CharField(label='ENTIDAD', required=True , widget=forms.TextInput(attrs={'placeholder': 'Entidad o Nombre Empresa'}))
    sector = forms.CharField(label='SECTOR', required=True , widget=forms.TextInput(attrs={'placeholder': 'Sector'}))
    fecha_inicial = forms.DateField(label='FECHA DE INICIO', widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    fecha_final = forms.DateField(label='FECHA TERMINACION', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    activo = forms.ChoiceField(label='ACTIVO', choices=[ ('', '---'), ('SI', 'SI'), ('NO', 'NO')], required=True)
    logro = forms.CharField(label='LOGROS', required=True, widget=forms.Textarea(attrs={'placeholder': 'Descripción de la Empresa'}))
    

    def __init__(self, *args, **kwargs):
        self.candidato_id = kwargs.pop('candidato_id', None)
        super(ExperienciaCandidatoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('estado_id_001'),
            ),
            Row(
                Column('entidad'),
            ),
            Row(
                Column('sector'),
            ),
            Row(
                Column('activo'),
            ),
            Row(
                Column('fecha_inicial'),
                Column('fecha_final'),
            ),
            Row(
                Column('logro'),
            ),
            Submit('submit', 'Guardar')
        )
    
    def clean(self):
        cleaned_data = super().clean()

        entidad = cleaned_data.get('entidad')
        sector = cleaned_data.get('sector')
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        activo = cleaned_data.get('activo')
        logro = cleaned_data.get('logro')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', entidad):
            self.add_error('entidad', "La entidad solo puede contener letras.")
        else:
            self.cleaned_data['entidad'] = entidad.upper()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', sector):
            self.add_error('sector', "La entidad solo puede contener letras.")
        else:
            self.cleaned_data['sector'] = entidad.upper()

        fecha_actual = timezone.now().date()

        if fecha_inicial:
            if fecha_inicial > fecha_actual:
                self.add_error({
                    'fecha_inicial': "La fecha inicial no puede ser mayor a la fecha actual."
                })

        if fecha_final:
            if fecha_final > fecha_actual:
                self.add_error({
                    'fecha_final': "La fecha final no puede ser mayor a la fecha actual."
                })

            if fecha_inicial and fecha_inicial > fecha_final:
                self.add_error({
                    'fecha_inicial': "La fecha inicial no puede ser mayor a la fecha final.",
                    'fecha_final': "La fecha final no puede ser menor a la fecha inicial."
                })

        if activo == 'NO':  # '2' representa 'NO' en ACTIVO_CHOICES
            if not fecha_final:
                self.add_error({
                    'fecha_final': "La fecha final es obligatoria si la experiencia no está activa."
                })

        if len(logro.split()) < 30:
            self.add_error('logro','La descripción debe contener al menos 30 palabras')

        return cleaned_data

    def save(self, candidato_id):
        estado_id_001 = self.cleaned_data['estado_id_001']
        entidad       = self.cleaned_data['entidad']
        sector        = self.cleaned_data['sector']
        fecha_inicial = self.cleaned_data['fecha_inicial']
        fecha_final   = self.cleaned_data['fecha_final']
        activo        = self.cleaned_data['activo']
        logro         = self.cleaned_data['logro']
        candidato_id_101 = Can101Candidato.objects.get(id=candidato_id)

        experiencia = Can102Experiencia(
            estado_id_001 = estado_id_001,
            entidad = entidad,
            sector = sector,
            fecha_inicial = fecha_inicial,
            fecha_final = fecha_final,
            activo = activo,
            logro = logro,
            candidato_id_101= candidato_id_101,
        )

        experiencia.save()