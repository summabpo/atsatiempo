import re
from django import forms
from django.utils import timezone
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Hidden, Div, Submit
from applications.common.models import Cat001Estado, Cat004Ciudad
from applications.candidato.models import Can101Candidato, Can103Educacion


from crispy_forms.layout import Layout, Layout, Div, Submit, HTML, Row, Column, Fieldset

from applications.services.choices import NIVEL_ESTUDIO_CHOICES_STATIC, ESTADO_ESTUDIOS_CHOICES_STATIC
from applications.vacante.models import Cli055ProfesionEstudio

class EstudioCandidatoForm(forms.Form):
    

    estado_id_001 = forms.ModelChoiceField(label='ESTADO', queryset=Cat001Estado.objects.all(), required=False)
    institucion = forms.CharField(label='INSTITUCION', required=True , widget=forms.TextInput(attrs={'placeholder': 'Institución'}))
    fecha_inicial = forms.DateField(label='FECHA DE INICIO', widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    fecha_final = forms.DateField(label='FECHA TERMINACION', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    # grado_en = forms.CharField(label='GRADO EN', required=False , widget=forms.TextInput(attrs={'placeholder': 'Grado en'}))
    grado_en = forms.BooleanField(
        label='¿GRADUADO?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    titulo = forms.CharField(label='TITULO', required=True , widget=forms.TextInput(attrs={'placeholder': 'Titulo'}))
    carrera = forms.CharField(label='CARRERA', required=True , widget=forms.TextInput(attrs={'placeholder': 'Carrera'}))
    fortaleza_adquiridas = forms.CharField(label='LOGROS', required=False, widget=forms.Textarea(attrs={'placeholder': 'Descripción de la Fortalezas'}))
    ciudad_id_004 = forms.ModelChoiceField(label='CIUDAD', queryset=Cat004Ciudad.objects.all(), required=True)
    tipo_estudio = forms.ChoiceField(label='TIPO DE ESTUDIO', choices=NIVEL_ESTUDIO_CHOICES_STATIC, required=True)

    def __init__(self, *args, **kwargs):
        self.candidato_id = kwargs.pop('candidato_id', None)
        super(EstudioCandidatoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_estudiocandidato'
        self.helper.form_class = 'container'
        
        self.fields['ciudad_id_004'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags':'true',
            'data-dropdown-parent': '#modal1, #modal2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })

        cities = Cat004Ciudad.objects.all().order_by('nombre')
        city_choices = [('', '----------')] + [(ciudad.id, f"{ciudad.nombre}") for ciudad in cities]

        self.fields['ciudad_id_004'] = forms.ChoiceField(
            label='CIUDAD',
            choices=city_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select ',  # Clases CSS del campo  
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccion una opción',
                    'data-dropdown-parent': '#modal1, #modal2',
                    }
        ), required=True)

        self.fields['tipo_estudio'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'data-dropdown-parent': '#modal1,#modal2',
            'data-hide-search': 'true',
            'class': 'form-select',
        })
        
        self.helper.layout = Layout(
            Div(
                Div('institucion', css_class='col'),
                Div('tipo_estudio', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('grado_en', css_class='col'),
                Div('fecha_inicial', css_class='col'),
                Div('fecha_final', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('titulo', css_class='col'),
                Div('carrera', css_class='col'),
                Div('ciudad_id_004', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('fortaleza_adquiridas', css_class='col'),
                css_class='row'
            ),
            
            # Div(
            #     Div('estado_id_001', css_class='col'),
            #     css_class='row'
            # ),
        )  
    
    def clean(self):
        cleaned_data =  super().clean()

        institucion = cleaned_data.get('institucion')
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        grado_en = cleaned_data.get('grado_en')
        titulo = cleaned_data.get('titulo')
        carrera = cleaned_data.get('carrera')
        fortaleza_adquiridas = cleaned_data.get('fortaleza_adquiridas')
        tipo_estudio = cleaned_data.get('tipo_estudio')
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', institucion):
            self.add_error('institucion', "La Instirución solo puede contener letras.")
        else:
            self.cleaned_data['institucion'] = institucion.upper()

        fecha_actual = timezone.now().date()


        if fecha_actual > fecha_inicial:
            if grado_en:
                if fecha_final is None or fecha_final == '':
                    self.add_error('fecha_final', "La fecha final no puede ir vacia si termino los estudios")
            
        else:
            self.add_error('fecha_inicial', "La fecha actual es mayot que la fecha inicial")

        # if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', grado_en):
        #     self.add_error('grado_en', "La Instirución solo puede contener letras.")
        # else:
        #     self.cleaned_data['grado_en'] = grado_en.upper()
        
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', titulo):
            self.add_error('titulo', "La Instirución solo puede contener letras.")
        else:
            self.cleaned_data['titulo'] = titulo.upper()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', carrera):
            self.add_error('carrera', "La Instirución solo puede contener letras.")
        else:
            self.cleaned_data['carrera'] = carrera.upper()
        
        if fortaleza_adquiridas and len(fortaleza_adquiridas.split()) < 5:
            self.add_error('fortaleza_adquiridas', 'La descripción debe contener al menos 5 palabras')

        return cleaned_data

    def save(self, candidato_id):

        if not self.is_valid():
            raise ValueError("El formulario no es válido")
    
        estado_id_001 = Cat001Estado.objects.get(id=1)
        institucion   = self.cleaned_data['institucion'] 
        fecha_inicial = self.cleaned_data['fecha_inicial']
        fecha_final   = self.cleaned_data['fecha_final']
        grado_en      = self.cleaned_data['grado_en']
        titulo        = self.cleaned_data['titulo']
        carrera       = self.cleaned_data['carrera']
        fortaleza_adquiridas = self.cleaned_data['fortaleza_adquiridas']
        tipo_estudio = self.cleaned_data['tipo_estudio']
        ciudad_id_004 = self.cleaned_data['ciudad_id_004']
        candidato_id_101 = Can101Candidato.objects.get(id=candidato_id)
        
        estudio = Can103Educacion(
            estado_id_001 = estado_id_001,
            institucion = institucion,
            fecha_inicial = fecha_inicial,
            fecha_final = fecha_final,
            grado_en = grado_en,
            titulo = titulo,
            carrera= carrera,
            fortaleza_adquiridas= fortaleza_adquiridas,
            ciudad_id_004= ciudad_id_004,
            candidato_id_101= candidato_id_101,
            tipo_estudio= tipo_estudio,
        )

        estudio.save()

class candidateStudyForm(forms.Form):
    institucion = forms.CharField(
        label='INSTITUCIÓN',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Institución', 'class': 'form-control'})
    )
    fecha_inicial = forms.DateField(
        label='FECHA INICIAL',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_final = forms.DateField(
        label='FECHA FINAL',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    titulo = forms.CharField(
        label='TÍTULO (Se refiere a la denominación oficial o el grado académico que se obtiene al completar exitosamente un programa de estudios y cumplir con todos los requisitos de graduación.)',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Título', 'class': 'form-control'})
    )
    carrera = forms.CharField(
        label='CARRERA (Se refiere al programa de estudios general o el campo disciplinar que se cursa en una institución educativa.)',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Carrera', 'class': 'form-control'})
    )
    # fortaleza_adquiridas = forms.CharField(
    #     label='FORTALEZAS ADQUIRIDAS',
    #     required=False,
    #     widget=forms.Textarea(attrs={'placeholder': 'Descripción de las fortalezas', 'class': 'form-control'})
    # )
    ciudad_id_004 = forms.ModelChoiceField(
        label='CIUDAD',
        queryset=Cat004Ciudad.objects.all(),
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-select', 
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
                'data-dropdown-parent': '#estudios_candidato',
            }
        )
    )
    tipo_estudio = forms.ChoiceField(
        label='TIPO DE ESTUDIO',
        choices=NIVEL_ESTUDIO_CHOICES_STATIC,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
                'data-dropdown-parent': '#estudios_candidato',
            }
        )
    )

    profesion_estudio = forms.ModelChoiceField(
        label='PROFESIÓN/ESTUDIO',
        queryset=Cli055ProfesionEstudio.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
                'data-dropdown-parent': '#estudios_candidato',
            }
        )
    )
    certificacion = forms.FileField(
        label='CERTIFICACIÓN',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    estado_estudios = forms.ChoiceField(
        label='ESTADO DEL ESTUDIO',
        choices=ESTADO_ESTUDIOS_CHOICES_STATIC,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
                'data-dropdown-parent': '#estudios_candidato',
            }
        )
    )

    

    

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

        # Si el formulario está en modo edición (es decir, tiene datos iniciales o instance)
        is_editing = bool(self.initial or self.instance)
        
        if is_editing:
            # Quitamos 'data-dropdown-parent' de los widgets select
            select_fields = ['tipo_estudio', 'ciudad_id_004', 'profesion_estudio', 'estado_estudios']
            for field_name in select_fields:
                field = self.fields.get(field_name)
                if field and hasattr(field.widget, 'attrs'):
                    field.widget.attrs.pop('data-dropdown-parent', None)
            
            # Hacer el campo de certificación opcional cuando se está editando
            self.fields['certificacion'].required = False
        
        # Si tipo_estudio es "Sin estudios" ('1'), hacer los demás campos opcionales
        tipo_estudio_value = None
        if self.data and 'tipo_estudio' in self.data:
            tipo_estudio_value = self.data.get('tipo_estudio')
        elif self.initial and 'tipo_estudio' in self.initial:
            tipo_estudio_value = self.initial.get('tipo_estudio')
        
        if tipo_estudio_value == '1':
            # Hacer todos los campos opcionales excepto tipo_estudio
            self.fields['institucion'].required = False
            self.fields['fecha_inicial'].required = False
            self.fields['ciudad_id_004'].required = False
            self.fields['certificacion'].required = False
        
        # Ajustar campos según estado_estudios
        estado_estudios_value = None
        if self.data and 'estado_estudios' in self.data:
            estado_estudios_value = self.data.get('estado_estudios')
        elif self.initial and 'estado_estudios' in self.initial:
            estado_estudios_value = self.initial.get('estado_estudios')
        
        if estado_estudios_value == 'G':
            # Si es Graduado, hacer obligatorios título, fecha_final
            self.fields['titulo'].required = True
            self.fields['fecha_final'].required = True
            self.fields['fecha_inicial'].required = True
            # Certificación será validada en clean()
        elif estado_estudios_value == 'A':
            # Si es Aplazado, hacer obligatoria fecha_final y ocultar fecha_inicial
            self.fields['fecha_final'].required = True
            self.fields['fecha_inicial'].required = False
            self.fields['titulo'].required = False
            self.fields['certificacion'].required = False
        elif estado_estudios_value == 'C':
            # Si está en curso, hacer opcionales título y fecha_final
            self.fields['titulo'].required = False
            self.fields['fecha_final'].required = False
            self.fields['fecha_inicial'].required = True
            self.fields['certificacion'].required = False
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_estudio'
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Información Académica</h4>"),
                    Div('institucion', css_class='col-12'),
                    Div('tipo_estudio', css_class='col-12'),
                    Div('profesion_estudio', css_class='col-12'),
                    Div('estado_estudios', css_class='col-12'),
                    Div('titulo', css_class='col-12 campo-graduado'),
                    Div('fecha_inicial', css_class='col-6 campo-no-aplazado'),
                    Div('fecha_final', css_class='col-6 campo-graduado campo-aplazado'),
                    Div('ciudad_id_004', css_class='col-12'),
                    # Div('carrera', css_class='col-12'),
                    Div('certificacion', css_class='col-12 campo-graduado'),
                    # Div('fortaleza_adquiridas', css_class='col-12'),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
            
        )

    
    def clean(self):
        cleaned_data = super().clean()
        tipo_estudio = cleaned_data.get('tipo_estudio')
        
        # Si es "Sin estudios" (tipo_estudio == '1'), no validar los demás campos
        if tipo_estudio == '1':
            # Permitir guardar sin validar los demás campos
            return cleaned_data
        
        # Si no es "Sin estudios", validar todos los campos normalmente
        institucion = cleaned_data.get('institucion')
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        titulo = cleaned_data.get('titulo')
        estado_estudios = cleaned_data.get('estado_estudios')
        # carrera = cleaned_data.get('carrera')
        # fortaleza_adquiridas = cleaned_data.get('fortaleza_adquiridas')
        ciudad_id_004 = cleaned_data.get('ciudad_id_004')
        certificacion = cleaned_data.get('certificacion')
        profesion_estudio = cleaned_data.get('profesion_estudio')

        if institucion and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', institucion):
            self.add_error('institucion', "La Instirución solo puede contener letras.")
        elif institucion:
            self.cleaned_data['institucion'] = institucion.upper()

        fecha_actual = timezone.now().date()

        # Validar fecha_inicial solo si está presente y no es Aplazado
        if fecha_inicial and estado_estudios != 'A':
            if fecha_inicial > fecha_actual:
                self.add_error('fecha_inicial', "La fecha inicial no puede ser mayor que la fecha actual.")

        # Si el estado es "Graduado" (G), validar campos obligatorios
        if estado_estudios == 'G':
            if fecha_inicial is None or fecha_inicial == '':
                self.add_error('fecha_inicial', "La fecha inicial es obligatoria si el estado es Graduado.")
            if fecha_final is None or fecha_final == '':
                self.add_error('fecha_final', "La fecha final es obligatoria si el estado es Graduado.")
            elif fecha_final < fecha_inicial:
                self.add_error('fecha_final', "La fecha final no puede ser menor que la fecha inicial.")

            if titulo is None or titulo == '':
                self.add_error('titulo', "El título es obligatorio si el estado es Graduado.")

            if titulo and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', titulo):
                self.add_error('titulo', "El titulo solo puede contener letras.")
            elif titulo:
                self.cleaned_data['titulo'] = titulo.upper()
            
            # Certificado obligatorio si está graduado
            is_editing = bool(self.initial)
            if not certificacion and not is_editing:
                self.add_error('certificacion', 'El archivo de certificación es obligatorio si el estado es Graduado.')
            
            # Si está graduado, no debe tener fecha_inicial oculta
            if not fecha_inicial:
                self.add_error('fecha_inicial', "La fecha inicial es obligatoria si el estado es Graduado.")
                
        elif estado_estudios == 'A':
            # Si es Aplazado, fecha_final es obligatoria
            if fecha_final is None or fecha_final == '':
                self.add_error('fecha_final', "La fecha final es obligatoria si el estado es Aplazado.")
            
            # Si fecha_inicial está presente (aunque esté oculto), validar que no sea mayor que fecha_final
            if fecha_inicial and fecha_final:
                if fecha_inicial > fecha_final:
                    self.add_error('fecha_final', "La fecha final no puede ser menor que la fecha inicial.")
            
            if titulo:
                self.add_error('titulo', "El título no debe estar presente si el estado es Aplazado.")
            
            # Certificación no debe estar presente si está aplazado
            # Si se está editando y hay una certificación existente, permitir que se elimine
            is_editing = bool(self.initial)
            if certificacion and not is_editing:
                self.add_error('certificacion', "La certificación no debe estar presente si el estado es Aplazado.")
            
            # Si no hay fecha_inicial, usar fecha_final como fecha_inicial (se manejará en la vista)
            if not fecha_inicial and fecha_final:
                # Permitir que se use fecha_final como fecha_inicial en la vista
                pass
                
        elif estado_estudios == 'C':
            # Si está en curso, no debe tener título ni fecha final
            if titulo:
                self.add_error('titulo', "El título no debe estar presente si el estado es En curso.")
            if fecha_final:
                self.add_error('fecha_final', "La fecha final no debe estar presente si el estado es En curso.")
            
            # Certificación no debe estar presente si está en curso
            # Si se está editando y hay una certificación existente, permitir que se elimine
            is_editing = bool(self.initial)
            if certificacion and not is_editing:
                self.add_error('certificacion', "La certificación no debe estar presente si el estado es En curso.")

        # Validar archivo de certificación si está presente
        if certificacion:
            if hasattr(certificacion, 'content_type'):
                if certificacion.content_type != 'application/pdf':
                    self.add_error('certificacion', 'El archivo debe ser un PDF.')
            if hasattr(certificacion, 'size'):
                if certificacion.size > 5 * 1024 * 1024:
                    self.add_error('certificacion', 'El archivo no debe pesar más de 5 MB.')

        if not profesion_estudio:
            self.add_error('profesion_estudio', 'Debe seleccionar una profesión o estudio.')

        return cleaned_data
