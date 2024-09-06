from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio
from applications.common.models import Cat004Ciudad

class VacanteForm(forms.Form):
    
    titulo = forms.CharField(label='TITULO DE LA VACANTE', required=True)
    numero_posiciones = forms.IntegerField(label="NUMERO VACANTES", required=True)
    profesion_estudio_id_055 = forms.CharField(label='PROFESION O ESTUDIANTE', required=True)
    experiencia_requerida = forms.CharField(label='EXPERIENCIA ', required=True, widget=forms.Textarea(attrs={'placeholder': 'Descripción de la Fortalezas'}))
    soft_skills_id_053 = forms.CharField(label='HABILIDADES BLANDAS', required=True)
    hard_skills_id_054 = forms.CharField(label='HABILIDADES FUERTES', required=True)
    funciones_responsabilidades = forms.CharField( label='FUNCIONES Y RESPONSABILIDADES', required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Tus logros empresariales',
                'rows': 5,  
                'cols': 40,  
                'class': 'fixed-size-textarea'
            }
        )
    )
    ciudad = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    salario = forms.IntegerField(label="NUMERO VACANTES", required=True)
    # estado_vacante 
    # estado_id_004
    # cliente_id_051 

    #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Información General',
                Row(
                    Column('titulo', css_class='form-group col-md-6 mb-0'),
                    Column('numero_posiciones', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'profesion_estudio_id_055',
                'experiencia_requerida',
            ),
            Fieldset(
                'Habilidades',
                'soft_skills_id_053',
                'hard_skills_id_054',
            ),
            Fieldset(
                'Detalles del Puesto',
                'funciones_responsabilidades',
                Row(
                    Column('ciudad', css_class='form-group col-md-6 mb-0'),
                    Column('salario', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Estado y Cliente',
                Row(
                    Column('estado_vacante', css_class='form-group col-md-4 mb-0'),
                    Column('estado_id_004', css_class='form-group col-md-4 mb-0'),
                    Column('cliente_id_051', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Submit('submit', 'Guardar Vacante', css_class='btn btn-primary')
        )

    def clean(self):
        cleaned_data =  super().clean()

        # Validate titulo
        titulo = cleaned_data.get('titulo')
        if not titulo:
            self.add_error('titulo', 'El título es obligatorio.')
        elif len(titulo) > 100:
            self.add_error('titulo', 'El título no puede exceder los 100 caracteres.')
        else:
            self.cleaned_data['institucion'] = titulo.upper()   

        # Validate numero_posiciones
        numero_posiciones = cleaned_data.get('numero_posiciones')
        if not numero_posiciones:
            self.add_error('numero_posiciones', 'El número de posiciones es obligatorio.')
        elif not isinstance(numero_posiciones, int) or numero_posiciones <= 0:
            self.add_error('numero_posiciones', 'El número de posiciones debe ser un entero positivo.')

        # Validate profesion_estudio_id_055
        profesion_estudio_id_055 = cleaned_data.get('profesion_estudio_id_055')
        if not profesion_estudio_id_055:
            self.add_error('profesion_estudio_id_055', 'La profesión o estudio es obligatorio.')

        # Validate experiencia_requerida
        experiencia_requerida = cleaned_data.get('experiencia_requerida')
        if not experiencia_requerida:
            self.add_error('experiencia_requerida', 'La experiencia requerida es obligatoria.')
        elif not isinstance(experiencia_requerida, int) or experiencia_requerida < 0:
            self.add_error('experiencia_requerida', 'La experiencia requerida debe ser un número entero no negativo.')

        # Validate soft_skills_id_053
        soft_skills_id_053 = cleaned_data.get('soft_skills_id_053')
        if not soft_skills_id_053:
            self.add_error('soft_skills_id_053', 'Las habilidades blandas son obligatorias.')

        # Validate hard_skills_id_054
        hard_skills_id_054 = cleaned_data.get('hard_skills_id_054')
        if not hard_skills_id_054:
            self.add_error('hard_skills_id_054', 'Las habilidades duras son obligatorias.')

        # Validate funciones_responsabilidades
        funciones_responsabilidades = cleaned_data.get('funciones_responsabilidades')
        if not funciones_responsabilidades:
            self.add_error('funciones_responsabilidades', 'Las funciones y responsabilidades son obligatorias.')
        elif len(funciones_responsabilidades) > 1000:
            self.add_error('funciones_responsabilidades', 'Las funciones y responsabilidades no pueden exceder los 1000 caracteres.')

        # Validate ciudad
        ciudad = cleaned_data.get('ciudad')
        if not ciudad:
            self.add_error('ciudad', 'La ciudad es obligatoria.')

        # Validate salario
        salario = cleaned_data.get('salario')
        if not salario:
            self.add_error('salario', 'El salario es obligatorio.')
        elif not isinstance(salario, (int, float)) or salario <= 0:
            self.add_error('salario', 'El salario debe ser un número positivo.')

        return cleaned_data