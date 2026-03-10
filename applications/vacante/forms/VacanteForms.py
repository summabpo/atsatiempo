import json
from datetime import date, timedelta
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText
from decimal import Decimal

#models
from applications.candidato.models import Can104Skill
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio, Cli075GrupoProfesion
from applications.common.models import Cat004Ciudad
from applications.cliente.models import Cli051Cliente, Cli068Cargo, Cli076GrupoFitCultural, Cli077FitCultural, Cli078MotivadoresCandidato
from applications.usuarios.models import UsuarioBase
from applications.vacante.models import Cli052Vacante


#choices
from applications.services.choices import EDAD_SELECT_CHOICES_STATIC, IDIOMA_CHOICES_STATIC, NIVEL_CHOICHES_STATIC, NIVEL_IDIOMA_CHOICES_STATIC, TIPO_CLIENTE_STATIC, EDAD_CHOICES_STATIC, GENERO_CHOICES_STATIC, TIEMPO_EXPERIENCIA_CHOICES_STATIC, MODALIDAD_CHOICES_STATIC, JORNADA_CHOICES_STATIC, TIPO_HORARIO_CHOICES_STATIC, TIPO_PROFESION_CHOICES_STATIC, TIPO_SALARIO_CHOICES_STATIC, FRECUENCIA_PAGO_CHOICES_STATIC, NIVEL_ESTUDIO_CHOICES_STATIC, TERMINO_CONTRATO_CHOICES_STATIC, HORARIO_CHOICES_STATIC, MOTIVO_VACANTE_CHOICES_STATIC


class CheckboxSelectMultipleWithTitle(forms.CheckboxSelectMultiple):
    """Widget que añade atributo title a cada checkbox para mostrar descripción al pasar el cursor."""
    def __init__(self, attrs=None, titles=None):
        super().__init__(attrs)
        self.titles = titles or {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value and str(value) in self.titles:
            title_text = self.titles[str(value)]
            if title_text:
                option['attrs']['title'] = title_text
        return option


class VacanteForm(forms.Form):
    # EXPERIENCIA_TIEMPO = [
    #     ('', 'Seleccione una opción... '),
    #     (1, '0 a 6 Meses'),
    #     (2, '1 año a 2 años'),
    #     (3, 'Más de 2 años'),
    #     (4, 'Sin experiencia'),
    # ]

    

    titulo = forms.CharField(label='TITULO DE LA VACANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)

    numero_posiciones = forms.IntegerField(label="NUMERO VACANTES",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)

    profesion_estudio_id_055 = forms.CharField(label='PROFESION O ESTUDIANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)

    experiencia_requerida = forms.ChoiceField(label='EXPERIENCIA ', choices = TIEMPO_EXPERIENCIA_CHOICES_STATIC, widget = forms.Select( attrs={ 'class': 'form-select form-select-solid fw-bold'}), required=True)
    soft_skills_id_053 = forms.CharField(label='HABILIDADES BLANDAS', 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo
                'id': 'soft_skills',  # ID del campo    
            }
        ), required=True)
    
    hard_skills_id_054 = forms.CharField(label='HABILIDADES FUERTES', 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo
                'id': 'hard_skills',  # ID del campo    
            }
        ), required=True)
    
    funciones_responsabilidades = forms.CharField( label='FUNCIONES Y RESPONSABILIDADES', required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Describa por favor las funciones y responsabilidades.',
                'rows': 5,  
                'cols': 30,  
                'class': 'fixed-size-textarea form-control-solid',
                'id': 'funciones_responsabilidades'
            }
        )
    )

    # ciudad = forms.ModelChoiceField(label='CIUDAD',
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-select form-control-solid',  # Clases CSS del campo  
    #             'data-control': 'select2',
    #             'data-placeholder': 'Select an option',
    #             'data-dropdown-parent': '#modal_vacante',
    #             }
    #     ), queryset=Cat004Ciudad.objects.all(), required=True)
    salario = forms.CharField(
        label="SALARIO",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese el salario, ej: 3.890.000'
        }),
        required=True
    )
    # estado_vacante 
    # estado_id_004
    # cliente_id_051 

    #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante'


        cities = Cat004Ciudad.objects.all().order_by('nombre')
        city_choices = [('', '----------')] + [(ciudad.id, f"{ciudad.nombre}") for ciudad in cities]

        self.fields['ciudad'] = forms.ChoiceField(
            label='CIUDAD',
            choices=city_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',  # Clases CSS del campo  
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccion una opción',
                    'data-dropdown-parent': '#modal_vacante',
                    }
        ), required=True)

        usuarios = UsuarioBase.objects.filter(group__id=6).order_by('primer_apellido')
        usuario_choices = [('', '----------')] + [(usuario.id, f"{usuario.primer_nombre} {usuario.segundo_nombre} {usuario.primer_apellido} {usuario.segundo_apellido}") for usuario in usuarios]

        self.fields['usuario_asignado'] = forms.ChoiceField(
            label='ANALISTA RESPONSABLE',
            choices=usuario_choices,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
                'data-dropdown-parent': '#modal_vacante',
                }
        ), required=True)

        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(
                    Column('titulo', css_class='form-group col-md-6 mb-0'),
                    Column('numero_posiciones', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'profesion_estudio_id_055',
                'experiencia_requerida',
            ),
            Fieldset(
                '',
                'soft_skills_id_053',
                'hard_skills_id_054',
            ),
            Fieldset(
                '',
                'funciones_responsabilidades',
                Row(
                    Column('ciudad', css_class='form-group col-md-6 mb-0'),
                    Column('salario', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                '',
                'usuario_asignado',
            ),
            
            # Submit('submit', 'Guardar Vacante', css_class='btn btn-primary')
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
        elif not str(numero_posiciones).isdigit() or int(numero_posiciones) <= 0:
            self.add_error('numero_posiciones', 'El número de posiciones debe ser un número positivo.')

        # Validate profesion_estudio_id_055
        profesion_estudio_id_055 = cleaned_data.get('profesion_estudio_id_055')
        if not profesion_estudio_id_055:
            self.add_error('profesion_estudio_id_055', 'La profesión o estudio es obligatorio.')

        # Validate experiencia_requerida
        experiencia_requerida = cleaned_data.get('experiencia_requerida')
        if not experiencia_requerida:
            self.add_error('experiencia_requerida', 'La experiencia requerida es obligatoria.')

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

        # Si salario es un valor vacío (None o ''), lo asignamos como None
        # Validate salario
        salario = cleaned_data.get('salario')

        print(salario)

        if salario:
            # Quitar comas, puntos (separador de miles) y signos de dólar
            salario_str = str(salario).replace(',', '').replace('.', '').replace('$', '').replace(' ', '')

            # Asegurarse que sea numérico
            if not salario_str.isdigit():
                raise forms.ValidationError("Ingrese un número válido para el salario.")

            # Convertir a Decimal y guardar
            cleaned_data['salario'] = Decimal(salario_str)
        else:
            cleaned_data['salario'] = None
            
                

        return cleaned_data  
class VacanteFormEdit(forms.Form):
    

    titulo = forms.CharField(label='TITULO DE LA VACANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)
    numero_posiciones = forms.IntegerField(label="NUMERO VACANTES",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)
    profesion_estudio_id_055 = forms.CharField(label='PROFESION O ESTUDIANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)
    experiencia_requerida = forms.ChoiceField(label='EXPERIENCIA ', choices = TIEMPO_EXPERIENCIA_CHOICES_STATIC, widget = forms.Select( attrs={ 'class': 'form-select form-select-solid fw-bold'}), required=True)
    soft_skills_id_053 = forms.CharField(label='HABILIDADES BLANDAS', 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo
                'id': 'soft_skills',  # ID del campo    
            }
        ), required=True)
    
    hard_skills_id_054 = forms.CharField(label='HABILIDADES FUERTES', 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo
                'id': 'hard_skills',  # ID del campo    
            }
        ), required=True)
    
    funciones_responsabilidades = forms.CharField( label='FUNCIONES Y RESPONSABILIDADES', required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Describa por favor las funciones y responsabilidades',
                'rows': 5,  
                'cols': 40,  
                'class': 'fixed-size-textarea form-control-solid',
                'id': 'funciones_responsabilidades'
            }
        )
    )

    # ciudad = forms.ModelChoiceField(label='CIUDAD',
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-select form-control-solid',  # Clases CSS del campo  
    #             'data-control': 'select2',
    #             'data-placeholder': 'Select an option',
    #             'data-dropdown-parent': '#modal_vacante',
    #             }
    #     ), queryset=Cat004Ciudad.objects.all(), required=True)
    salario = forms.CharField(
        label="SALARIO",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese el salario, ej: 3.890.000'
        }),
        required=True
    )
    # estado_vacante 
    # estado_id_004
    # cliente_id_051 

    #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante_edit'


        cities = Cat004Ciudad.objects.all().order_by('nombre')
        city_choices = [('', '----------')] + [(ciudad.id, f"{ciudad.nombre}") for ciudad in cities]

        self.fields['ciudad'] = forms.ChoiceField(
            label='CIUDAD',
            choices=city_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',  # Clases CSS del campo  
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccion una opción',
                    }
        ), required=True)

        usuarios = UsuarioBase.objects.filter(group__id=6).order_by('primer_apellido')
        usuario_choices = [('', '----------')] + [(usuario.id, f"{usuario.primer_nombre} {usuario.segundo_nombre} {usuario.primer_apellido} {usuario.segundo_apellido}") for usuario in usuarios]

        self.fields['usuario_asignado'] = forms.ChoiceField(
            label='ANALISTA RESPONSABLE',
            choices=usuario_choices,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
                }
        ), required=True)

        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(
                    Column('titulo', css_class='form-group col-md-6 mb-0'),
                    Column('numero_posiciones', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'profesion_estudio_id_055',
                'experiencia_requerida',
            ),
            Fieldset(
                '',
                'soft_skills_id_053',
                'hard_skills_id_054',
            ),
            Fieldset(
                '',
                'funciones_responsabilidades',
                Row(
                    Column('ciudad', css_class='form-group col-md-6 mb-0'),
                    Column('salario', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                '',
                'usuario_asignado',
            ),
            
            # Submit('submit', 'Guardar Vacante', css_class='btn btn-primary')
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
        elif not str(numero_posiciones).isdigit() or int(numero_posiciones) <= 0:
            self.add_error('numero_posiciones', 'El número de posiciones debe ser un número positivo.')

        # Validate profesion_estudio_id_055
        profesion_estudio_id_055 = cleaned_data.get('profesion_estudio_id_055')
        if not profesion_estudio_id_055:
            self.add_error('profesion_estudio_id_055', 'La profesión o estudio es obligatorio.')

        # Validate experiencia_requerida
        experiencia_requerida = cleaned_data.get('experiencia_requerida')
        if not experiencia_requerida:
            self.add_error('experiencia_requerida', 'La experiencia requerida es obligatoria.')

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
        salario = self.cleaned_data.get('salario')
        
        if salario:
            salario = salario.replace('.', '')
            salario = salario.replace(',', '.')  # Reemplazar la coma por un punto    
        else:
            salario = None
        

        return cleaned_data
class VacanteAdicionalForms(forms.Form):
    

    titulo = forms.CharField(label='TITULO DE LA VACANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)
    numero_posiciones = forms.IntegerField(label="NUMERO VACANTES",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)
    profesion_estudio_id_055 = forms.CharField(label='PROFESION O ESTUDIANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=True)
    experiencia_requerida = forms.ChoiceField(label='EXPERIENCIA ', choices = TIEMPO_EXPERIENCIA_CHOICES_STATIC, widget = forms.Select( attrs={ 'class': 'form-select form-select-solid fw-bold'}), required=True)
    soft_skills_id_053 = forms.CharField(label='HABILIDADES BLANDAS', 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo
                'id': 'soft_skills',  # ID del campo    
            }
        ), required=True)
    
    hard_skills_id_054 = forms.CharField(label='HABILIDADES FUERTES', 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo
                'id': 'hard_skills',  # ID del campo    
            }
        ), required=True)
    
    funciones_responsabilidades = forms.CharField( label='FUNCIONES Y RESPONSABILIDADES', required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Describa por favor las funciones y responsabilidades',
                'rows': 5,  
                'cols': 30,  
                'class': 'fixed-size-textarea form-control-solid',
                'id': 'funciones_responsabilidades',
            }
        )
    )

    # ciudad = forms.ModelChoiceField(label='CIUDAD',
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-select form-control-solid',  # Clases CSS del campo  
    #             'data-control': 'select2',
    #             'data-placeholder': 'Select an option',
    #             'data-dropdown-parent': '#modal_vacante',
    #             }
    #     ), queryset=Cat004Ciudad.objects.all(), required=True)
    salario = forms.CharField(
        label="SALARIO",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese el salario, ej: 3.890.000'
        }),
        required=True
    )
    # estado_vacante 
    # estado_id_004
    # cliente_id_051 

    #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante'


        cities = Cat004Ciudad.objects.all().order_by('nombre')
        city_choices = [('', '----------')] + [(ciudad.id, f"{ciudad.nombre}") for ciudad in cities]

        self.fields['ciudad'] = forms.ChoiceField(
            label='CIUDAD',
            choices=city_choices,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
                'data-dropdown-parent': '#modal_vacante',
                }
        ), required=True)

        clientes = Cli051Cliente.objects.all().order_by('razon_social')
        cliente_choices = [('', '----------')] + [(cliente.id, f"{cliente.razon_social}") for cliente in clientes]

        self.fields['cliente_id_051'] = forms.ChoiceField(
            label='CLIENTE',
            choices=cliente_choices,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
                'data-dropdown-parent': '#modal_vacante',
                }
        ), required=True)

        usuarios = UsuarioBase.objects.filter(group__id=6).order_by('primer_apellido')
        usuario_choices = [('', '----------')] + [(usuario.id, f"{usuario.primer_nombre} {usuario.segundo_nombre} {usuario.primer_apellido} {usuario.segundo_apellido}") for usuario in usuarios]

        self.fields['usuario_asignado'] = forms.ChoiceField(
            label='ANALISTA RESPONSABLE',
            choices=usuario_choices,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
                'data-dropdown-parent': '#modal_vacante',
                }
        ), required=True)

        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(
                    Column('cliente_id_051', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('titulo', css_class='form-group col-md-6 mb-0'),
                    Column('numero_posiciones', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'profesion_estudio_id_055',
                'experiencia_requerida',
            ),
            Fieldset(
                '',
                'soft_skills_id_053',
                'hard_skills_id_054',
            ),
            Fieldset(
                '',
                'funciones_responsabilidades',
                Row(
                    Column('ciudad', css_class='form-group col-md-6 mb-0'),
                    Column('salario', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                '',
                'usuario_asignado',
                
            ),
            
            # Submit('submit', 'Guardar Vacante', css_class='btn btn-primary')
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
        elif not str(numero_posiciones).isdigit() or int(numero_posiciones) <= 0:
            self.add_error('numero_posiciones', 'El número de posiciones debe ser un número positivo.')

        # Validate profesion_estudio_id_055
        profesion_estudio_id_055 = cleaned_data.get('profesion_estudio_id_055')
        if not profesion_estudio_id_055:
            self.add_error('profesion_estudio_id_055', 'La profesión o estudio es obligatorio.')

        # Validate experiencia_requerida
        experiencia_requerida = cleaned_data.get('experiencia_requerida')
        if not experiencia_requerida:
            self.add_error('experiencia_requerida', 'La experiencia requerida es obligatoria.')

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

        # Si salario es un valor vacío (None o ''), lo asignamos como None
        # Validate salario
        salario = self.cleaned_data.get('salario')
    
        if salario:
            # Eliminar puntos y espacios si están presentes
            salario = salario.replace('.', '').replace(' ', '')
            
            # Verificar si el salario es un número válido
            if not salario.isdigit():
                raise forms.ValidationError("Ingrese un número válido para el salario.")

            # Convertir el salario a un entero
            cleaned_data['salario'] =  int(salario)
        
        else:
            cleaned_data['salario'] = None
            
                

        return cleaned_data
    
class VacancyFormAll(forms.Form):
    
    titulo = forms.CharField(label='TITULO DE LA VACANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=False)
    
    numero_posiciones = forms.ChoiceField(
        label="NUMERO VACANTES",
        choices=[(i, str(i)) for i in range(1, 11)],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )
    
    funciones_responsabilidades = forms.CharField( label='FUNCIONES Y RESPONSABILIDADES', required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese las funciones y responsabilidades',
                'id': 'id_funciones_responsabilidades'  # Asegura que coincida con el ID en el JS
            }
        )
    )
    
    def __init__(self, *args, cliente_id=None, **kwargs):
        super(VacancyFormAll, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante_cliente'


        TIPO_CLIENTE = [('', 'Seleccione un tipo de cliente')] + [(str(tipo[0]), tipo[1]) for tipo in TIPO_CLIENTE_STATIC]

        self.fields['tipo_cliente'] = forms.ChoiceField(
            label='TIPO DE CLIENTE',
            choices=TIPO_CLIENTE,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
            }
            ), required=False)


        if cliente_id:
            cargos = Cli068Cargo.objects.filter(cliente=cliente_id).order_by('nombre_cargo')
        else:
            cargos = Cli068Cargo.objects.none()

        cargo_choices = [('', '----------')] + [(cargo.id, f"{cargo.nombre_cargo}") for cargo in cargos]
        
        self.fields['cargo'] = forms.ChoiceField(
            label='CARGO',
            choices=cargo_choices,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',  # Clases CSS del campo  
            'data-control': 'select2',
            'data-placeholder': 'Seleccion una opción',
            }
        ), required=False)

        

        self.fields['edad_inicial'] = forms.ChoiceField(
            label='EDAD INICIAL',
            choices=EDAD_SELECT_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['edad_final'] = forms.ChoiceField(
            label='EDAD FINAL',
            choices=EDAD_SELECT_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['genero'] = forms.ChoiceField(
            label='GÉNERO',
            choices=GENERO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['tiempo_experiencia'] = forms.ChoiceField(
            label='TIEMPO DE EXPERIENCIA',
            choices=TIEMPO_EXPERIENCIA_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['horario_inicio'] = forms.ChoiceField(
            label='HORARIO INICIO',
            choices=HORARIO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ),
            required=False
        )

        self.fields['horario_final'] = forms.ChoiceField(
            label='HORARIO FINAL',
            choices=HORARIO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ),
            required=False
        )

        self.fields['hora_inicio'] = forms.TimeField(
            label='HORA INICIO',
            widget=forms.TimeInput(
            attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese la hora de inicio',
            'type': 'time'
            }
            ),
            required=False
        )

        self.fields['hora_final'] = forms.TimeField(
            label='HORA FINAL',
            widget=forms.TimeInput(
            attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese la hora final',
            'type': 'time'
            }
            ),
            required=False
        )

        self.fields['modalidad'] = forms.ChoiceField(
            label='MODALIDAD',
            choices=MODALIDAD_CHOICES_STATIC,
            widget=forms.Select(
            
            ), required=False)

        self.fields['jornada'] = forms.ChoiceField(
            label='JORNADA',
            choices=JORNADA_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['salario'] = forms.CharField(
            label='SALARIO',
            widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el salario',
                'x-data': '{}',
                'x-mask:dynamic': "$money($input, ',', '.', 0)",  # <-- sin decimales si no los necesitas
                'id': 'id_salario'
                }
            ), required=False)

        self.fields['tipo_salario'] = forms.ChoiceField(
            label='TIPO DE SALARIO',
            choices=TIPO_SALARIO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['frecuencia_pago'] = forms.ChoiceField(
            label='FRECUENCIA DE PAGO',
            choices=FRECUENCIA_PAGO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['salario_adicional'] = forms.DecimalField(
            label='SALARIO ADICIONAL',
            widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el salario adicional',
                'x-data': '{}',
                'x-mask:dynamic': "$money($input, ',', '.', 4)",  # <-- sin decimales si no los necesitas
                'id': 'id_salario_adicional'
            }
            ), required=False)

        self.fields['idioma'] = forms.ChoiceField(
            label='IDIOMA',
            choices=IDIOMA_CHOICES_STATIC,
            widget=forms.Select(
                attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un idioma',
                }
            ), required=False)

        PROFESION_CHIOCE = [('', 'Seleccione una opción... ')] + [(profesion.id, profesion.nombre) for profesion in Cli055ProfesionEstudio.objects.all()]
        self.fields['profesion_estudio'] = forms.ChoiceField(
            label='PROFESIÓN O ESTUDIO',
            choices=PROFESION_CHIOCE,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['nivel_estudio'] = forms.ChoiceField(
            label='NIVEL DE ESTUDIO',
            choices=NIVEL_ESTUDIO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        lugares_trabajo = Cat004Ciudad.objects.all().order_by('nombre')
        lugar_trabajo_choices = [('', '----------')] + [(lugar.id, f"{lugar.nombre}") for lugar in lugares_trabajo]

        self.fields['lugar_trabajo'] = forms.ChoiceField(
            label='CIUDAD',
            choices=lugar_trabajo_choices,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

        self.fields['termino_contrato'] = forms.ChoiceField(
            label='TÉRMINO DE CONTRATO',
            choices=TERMINO_CONTRATO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)
        
        self.fields['soft_skills'] = forms.CharField(
            label='HABILIDADES BLANDAS',
            widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese las habilidades blandas',
                'id': 'id_soft_skills'  # Asegura que coincida con el ID en el JS
            }
            ),
            required=False
        )

        self.fields['hard_skills'] = forms.CharField(
            label='HABILIDADES FUERTES',
            widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese las habilidades fuertes',
                'id': 'id_hard_skills'  # Asegura que coincida con el ID en el JS
            }
            ),
            required=False
        )

        self.fields['descripcion_vacante'] = forms.CharField(
            label='DESCRIPCIÓN DE LA VACANTE',
            widget=forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese la descripción de la vacante',
                    'rows': 5,
                    'cols': 30,
                    'id': 'id_descripcion_vacante'
                }
            ),
            required=False
        )

        self.fields['nivel_idioma'] = forms.ChoiceField(
            label='NIVEL DE IDIOMA',
            choices=NIVEL_IDIOMA_CHOICES_STATIC,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccione una opción',
                }
            ),
            required=False
        )

        self.fields['estudios_complementarios'] = forms.CharField(
            label='ESTUDIOS COMPLEMENTARIOS',
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese los estudios complementarios',
                }
            ),
            required=False
        )

        self.fields['estudios_complementarios_certificado'] = forms.ChoiceField(
            label='CERTIFICADO',
            choices=[(True, 'Sí'), (False, 'No')],
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ),
            required=False
        )

        self.fields['cantidad_presentar'] = forms.ChoiceField(
            label='CANTIDAD A PRESENTAR',
            choices=[(i, str(i)) for i in range(1, 11)],
            widget=forms.Select(
            attrs={
                'class': 'form-select form-control-solid',
                'placeholder': 'Seleccione la cantidad a presentar',
            }
            ),
            required=False
        )

        self.fields['fecha_presentacion'] = forms.DateField(
            label='FECHA DE PRESENTACIÓN',
            widget=forms.DateInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la fecha de presentación',
                'type': 'date'
            }
            ),
            required=False
        )

        self.fields['estado_estudio'] = forms.ChoiceField(
            label='¿GRADUADO?',
            choices=[(True, 'Sí'), (False, 'No')],
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ),
            required=False
        )

        self.fields['barrio'] = forms.CharField(
            label='BARRIO',
            max_length=100,
            required=False,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese el barrio',
                }
            )
        )

        self.fields['direccion'] = forms.CharField(
            label='DIRECCIÓN',
            max_length=100,
            required=False,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese la dirección',
                }
            )
        )

        self.fields['url_mapa'] = forms.URLField(
            label='URL DEL MAPA',
            required=False,
            widget=forms.URLInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese la URL del mapa',
                }
            )
        )
        
        self.helper.layout = Layout(
            # 🏗️ DATOS GENERALES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Datos Principales</h4>"),
                    Div('titulo', css_class='col-12'),  # Título
                    Div('cargo', css_class='col-12'),  # Cargo
                    Div('numero_posiciones', css_class='col-4'),  # Número de vacantes
                    Div('cantidad_presentar', css_class='col-4'),  # Número a presentar
                    Div('fecha_presentacion', css_class='col-4'),  # Fecha de presentación
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💼 DETALLES DEL TRABAJO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Detalles del Trabajo</h4>"),
                    Div('termino_contrato', css_class='col-3'),  # Término de contrato
                    Div('tiempo_experiencia', css_class='col-3'),  # Tiempo de experiencia
                    Div('modalidad', css_class='col-3'),  # Modalidad
                    Div('jornada', css_class='col-3'),  # Jornada
                    Div('horario_inicio', css_class='col-3'),  # Horario
                    Div('horario_final', css_class='col-3'),  # Horario
                    Div('hora_inicio', css_class='col-3'),  # Horario
                    Div('hora_final', css_class='col-3'),  # Horario
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💼 LUGAR DEL TRABAJO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Lugar de Trabajo</h4>"),
                    Div('lugar_trabajo', css_class='col-6'),  # Lugar de trabajo
                    Div('barrio', css_class='col-6'),  # Barrio
                    Div('direccion', css_class='col-6'),  # Dirección
                    Div('url_mapa', css_class='col-6'),  # URL del mapa
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 🛠️ REQUISITOS Y HABILIDADES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Requisitos y Habilidades</h4>"),
                    Div('soft_skills', css_class='col-6'),  # Habilidades blandas
                    Div('hard_skills', css_class='col-6'),  # Habilidades duras
                    Div('idioma', css_class='col-6'),  # Idioma
                    Div('nivel_idioma', css_class='col-6'),  # nivel_idioma
                    Div('profesion_estudio', css_class='col-6'),  # Profesión o estudio
                    Div('nivel_estudio', css_class='col-4'),  # Nivel de estudio
                    Div('estado_estudio', css_class='col-2'),  # Estado de estudio
                    Div('edad_inicial', css_class='col-3'),  # Edad Inicial
                    Div('edad_final', css_class='col-3'),  # Edad Final
                    Div('genero', css_class='col-6'),  # genero
                    Div('estudios_complementarios', css_class='col-9'),  # estudios_complementarios
                    Div('estudios_complementarios_certificado', css_class='col-3'),  # estudios_complementarios_certificado
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💰 INFORMACIÓN SALARIAL
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Información Salarial</h4>"),
                    Div(
                        PrependedText('salario', '$', placeholder='0.00'),
                        css_class='col-6'
                    ),  # Salario
                    Div('tipo_salario', css_class='col-6'),  # Tipo de salario
                    Div('frecuencia_pago', css_class='col-6'),  # Frecuencia de pago
                    Div(
                        PrependedText('salario_adicional', '$', placeholder='0.00'),
                        css_class='col-6'
                    ),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 📑 RESPONSABILIDADES DEL CARGO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Responsabilidades del Cargo</h4>"),
                    Div('funciones_responsabilidades', css_class='col-12'),  # Funciones y responsabilidades
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 🏗️ DESCRIPCION DE LA VACANTE
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Descripción de la Vacante</h4>"),
                    Div('descripcion_vacante', css_class='col-12'),  # Número de vacantes
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

        
    def clean(self):
        cleaned_data = super().clean()
        # Validate titulo
        titulo = cleaned_data.get('titulo').upper() if cleaned_data.get('titulo') else ''
        if not titulo:
            self.add_error('titulo', 'El título es obligatorio.')
        elif len(titulo.split()) > 10:
            self.add_error('titulo', 'El título no puede exceder las 10 palabras.')

        #validate cargo
        cargo = cleaned_data.get('cargo')
        if not cargo:
            self.add_error('cargo', 'El cargo es obligatorio.')


        # Validate descripcion_vacante
        descripcion_vacante = cleaned_data.get('descripcion_vacante')
        if not descripcion_vacante:
            self.add_error('descripcion_vacante', 'La descripción de la vacante es obligatoria.')
        elif len(descripcion_vacante.split()) < 5:
            self.add_error('descripcion_vacante', 'La descripción de la vacante debe tener al menos 5 palabras.')

        # Validate funciones_responsabilidades
        funciones_responsabilidades = cleaned_data.get('funciones_responsabilidades')
        if not funciones_responsabilidades:
            self.add_error('funciones_responsabilidades', 'Las funciones y responsabilidades son obligatorias.')

        # Validate horario_inicio
        horario_inicio = cleaned_data.get('horario_inicio')
        if not horario_inicio:
            self.add_error('horario_inicio', 'El horario de inicio es obligatorio.')
        
        # Validate horario_final
        horario_final = cleaned_data.get('horario_final')
        if not horario_final:
            self.add_error('horario_final', 'El horario final es obligatorio.')
        
        # Validate hora_inicio
        hora_inicio = cleaned_data.get('hora_inicio')
        if not hora_inicio:
            self.add_error('hora_inicio', 'La hora de inicio es obligatoria.')
        
        # Validate hora_final
        hora_final = cleaned_data.get('hora_final')
        if not hora_final:
            self.add_error('hora_final', 'La hora final es obligatoria.')
        
        

        # Validate edad
        edad_inicial = cleaned_data.get('edad_inicial')
        edad_final = cleaned_data.get('edad_final')
        if not edad_inicial:
            self.add_error('edad_inicial', 'La edad inicial es obligatoria.')
        if not edad_final:
            self.add_error('edad_final', 'La edad final es obligatoria.')
        if edad_inicial and edad_final and int(edad_inicial) > int(edad_final):
            self.add_error('edad_final', 'La edad final debe ser mayor o igual a la edad inicial.')

        # Validate genero
        genero = cleaned_data.get('genero')
        if not genero:
            self.add_error('genero', 'El género es obligatorio.')

        # Validate tiempo_experiencia
        tiempo_experiencia = cleaned_data.get('tiempo_experiencia')
        if not tiempo_experiencia:
            self.add_error('tiempo_experiencia', 'El tiempo de experiencia es obligatorio.')

        # Validate modalidad
        modalidad = cleaned_data.get('modalidad')
        if not modalidad:
            self.add_error('modalidad', 'La modalidad es obligatoria.')

        # Validate jornada
        jornada = cleaned_data.get('jornada')
        if not jornada:
            self.add_error('jornada', 'La jornada es obligatoria.')

        # Validate salario
        salario = cleaned_data.get('salario')
        if salario:
            salario = salario.replace('.', '')
            salario = salario.replace(',', '.')
            print(salario)
            cleaned_data['salario'] = salario
        else:
            print('No hay salario')
            
        # Validate tipo_salario
        tipo_salario = cleaned_data.get('tipo_salario')
        if not tipo_salario:
            self.add_error('tipo_salario', 'El tipo de salario es obligatorio.')

        # Validate frecuencia_pago
        frecuencia_pago = cleaned_data.get('frecuencia_pago')
        if not frecuencia_pago:
            self.add_error('frecuencia_pago', 'La frecuencia de pago es obligatoria.')

        # Validate salario_adicional
        salario_adicional = cleaned_data.get('salario_adicional')
        if salario_adicional:
            # Eliminar puntos y signo $
            salario_adicional = str(salario_adicional).replace('.', '').replace('$', '').replace(' ', '')
            
            # Verificar si el salario adicional es un número válido
            if not salario_adicional.isdigit():
                self.add_error('salario_adicional', 'Ingrese un número válido para el salario adicional.')
            else:
                # Convertir el salario adicional a un decimal
                cleaned_data['salario_adicional'] = Decimal(salario_adicional)
        else:
            cleaned_data['salario_adicional'] = None
    
        # Validate idioma
        idioma = cleaned_data.get('idioma')
        if not idioma:
            self.add_error('idioma', 'El idioma es obligatorio.')

        # Validate nivel_idioma
        nivel_idioma = cleaned_data.get('nivel_idioma')
        if not nivel_idioma:
            self.add_error('nivel_idioma', 'El nivel de idioma es obligatorio.')

        # Validate profesion_estudio
        profesion_estudio = cleaned_data.get('profesion_estudio')
        if not profesion_estudio:
            self.add_error('profesion_estudio', 'La profesión o estudio es obligatorio.')

        # Validate nivel_estudio
        nivel_estudio = cleaned_data.get('nivel_estudio')
        if not nivel_estudio:
            self.add_error('nivel_estudio', 'El nivel de estudio es obligatorio.')

        # Validate lugar_trabajo
        lugar_trabajo = cleaned_data.get('lugar_trabajo')
        if not lugar_trabajo:
            self.add_error('lugar_trabajo', 'El lugar de trabajo es obligatorio.')

        # Validate termino_contrato
        termino_contrato = cleaned_data.get('termino_contrato')
        if not termino_contrato:
            self.add_error('termino_contrato', 'El término de contrato es obligatorio.')

        # Validate soft_skills
        soft_skills = cleaned_data.get('soft_skills')
        if not soft_skills:
            self.add_error('soft_skills', 'Las habilidades blandas son obligatorias.')

        # Validate hard_skills
        hard_skills = cleaned_data.get('hard_skills')
        if not hard_skills:
            self.add_error('hard_skills', 'Las habilidades duras son obligatorias.')

        # Validate estudios_complementarios
        estudios_complementarios = cleaned_data.get('estudios_complementarios')
        if estudios_complementarios and len(estudios_complementarios) > 255:
            self.add_error('estudios_complementarios', 'Los estudios complementarios no pueden exceder los 255 caracteres.')

        # Validate estudios_complementarios_certificado
        estudios_complementarios_certificado = cleaned_data.get('estudios_complementarios_certificado')
        if estudios_complementarios and estudios_complementarios_certificado is None:
            self.add_error('estudios_complementarios_certificado', 'Debe indicar si los estudios complementarios están certificados.')

        return cleaned_data
    

class VacancyFormEdit(forms.Form):
    titulo = forms.CharField(
        label='TITULO DE LA VACANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
            }
        ),
        required=False
    )

    numero_posiciones = forms.ChoiceField(
        label="NUMERO VACANTES",
        choices=[(i, str(i)) for i in range(1, 11)],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    funciones_responsabilidades = forms.CharField(
        label='FUNCIONES Y RESPONSABILIDADES',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese las funciones y responsabilidades',
                'id': 'id_funciones_responsabilidades'
            }
        )
    )

    tipo_cliente = forms.ChoiceField(
        label='TIPO DE CLIENTE',
        choices=[('', 'Seleccione un tipo de cliente')] + [(str(tipo[0]), tipo[1]) for tipo in TIPO_CLIENTE_STATIC],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
            }
        ),
        required=False
    )

    cargo = forms.ChoiceField(
        label='CARGO',
        choices=[],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
            }
        ),
        required=False
    )

    edad_inicial = forms.ChoiceField(
        label='EDAD INICIAL',
        choices=EDAD_SELECT_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    edad_final = forms.ChoiceField(
        label='EDAD FINAL',
        choices=EDAD_SELECT_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    genero = forms.ChoiceField(
        label='GÉNERO',
        choices=GENERO_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    tiempo_experiencia = forms.ChoiceField(
        label='TIEMPO DE EXPERIENCIA',
        choices=TIEMPO_EXPERIENCIA_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    horario_inicio = forms.ChoiceField(
        label='HORARIO INICIO',
        choices=HORARIO_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    horario_final = forms.ChoiceField(
        label='HORARIO FINAL',
        choices=HORARIO_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    hora_inicio = forms.TimeField(
        label='HORA INICIO',
        widget=forms.TimeInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la hora de inicio',
                'type': 'time'
            }
        ),
        required=False
    )

    hora_final = forms.TimeField(
        label='HORA FINAL',
        widget=forms.TimeInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la hora final',
                'type': 'time'
            }
        ),
        required=False
    )

    modalidad = forms.ChoiceField(
        label='MODALIDAD',
        choices=MODALIDAD_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    jornada = forms.ChoiceField(
        label='JORNADA',
        choices=JORNADA_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    salario = forms.CharField(
        label='SALARIO',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el salario',
                'x-data': '{}',
                'x-mask:dynamic': "$money($input, ',', '.', 0)",
                'id': 'id_salario'
            }
        ),
        required=False
    )

    tipo_salario = forms.ChoiceField(
        label='TIPO DE SALARIO',
        choices=TIPO_SALARIO_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    frecuencia_pago = forms.ChoiceField(
        label='FRECUENCIA DE PAGO',
        choices=FRECUENCIA_PAGO_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    salario_adicional = forms.DecimalField(
        label='SALARIO ADICIONAL',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el salario adicional',
                'x-data': '{}',
                'x-mask:dynamic': "$money($input, ',', '.', 4)",
                'id': 'id_salario_adicional'
            }
        ),
        required=False
    )

    idioma = forms.ChoiceField(
        label='IDIOMA',
        choices=IDIOMA_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un idioma',
            }
        ),
        required=False
    )

    profesion_estudio = forms.ChoiceField(
        label='PROFESIÓN O ESTUDIO',
        choices=[('', 'Seleccione una opción... ')] + [(profesion.id, profesion.nombre) for profesion in Cli055ProfesionEstudio.objects.all()],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    nivel_estudio = forms.ChoiceField(
        label='NIVEL DE ESTUDIO',
        choices=NIVEL_ESTUDIO_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    lugar_trabajo = forms.ChoiceField(
        label='CIUDAD',
        choices=[('', '----------')] + [(lugar.id, f"{lugar.nombre}") for lugar in Cat004Ciudad.objects.all().order_by('nombre')],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    termino_contrato = forms.ChoiceField(
        label='TÉRMINO DE CONTRATO',
        choices=TERMINO_CONTRATO_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    soft_skills = forms.CharField(
        label='HABILIDADES BLANDAS',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese las habilidades blandas',
                'id': 'id_soft_skills'
            }
        ),
        required=False
    )

    hard_skills = forms.CharField(
        label='HABILIDADES FUERTES',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese las habilidades fuertes',
                'id': 'id_hard_skills'
            }
        ),
        required=False
    )

    descripcion_vacante = forms.CharField(
        label='DESCRIPCIÓN DE LA VACANTE',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la descripción de la vacante',
                'rows': 5,
                'cols': 30,
                'id': 'id_descripcion_vacante'
            }
        ),
        required=False
    )

    nivel_idioma = forms.ChoiceField(
        label='NIVEL DE IDIOMA',
        choices=NIVEL_IDIOMA_CHOICES_STATIC,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    estudios_complementarios = forms.CharField(
        label='ESTUDIOS COMPLEMENTARIOS',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese los estudios complementarios',
            }
        ),
        required=False
    )

    estudios_complementarios_certificado = forms.ChoiceField(
        label='CERTIFICADO',
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    cantidad_presentar = forms.ChoiceField(
        label='CANTIDAD A PRESENTAR',
        choices=[(i, str(i)) for i in range(1, 11)],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-control-solid',
                'placeholder': 'Seleccione la cantidad a presentar',
            }
        ),
        required=False
    )

    fecha_presentacion = forms.DateField(
        label='FECHA DE PRESENTACIÓN',
        widget=forms.DateInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la fecha de presentación',
                'type': 'date'
            }
        ),
        required=False
    )

    estado_estudio = forms.ChoiceField(
        label='¿GRADUADO?',
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=False
    )

    barrio = forms.CharField(
        label='BARRIO',
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el barrio',
            }
        )
    )

    direccion = forms.CharField(
        label='DIRECCIÓN',
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la dirección',
            }
        )
    )

    url_mapa = forms.URLField(
        label='URL DEL MAPA',
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la URL del mapa',
            }
        )
    )

    def __init__(self, *args, cliente_id=None, **kwargs):
        super(VacancyFormEdit, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante_edit'

        TIPO_CLIENTE = [('', 'Seleccione un tipo de cliente')] + [(str(tipo[0]), tipo[1]) for tipo in TIPO_CLIENTE_STATIC]

        self.fields['tipo_cliente'] = forms.ChoiceField(
            label='TIPO DE CLIENTE',
            choices=TIPO_CLIENTE,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccion una opción',
                }
            ),
            required=False
        )

        if cliente_id:
            cargos = Cli068Cargo.objects.filter(cliente=cliente_id).order_by('nombre_cargo')
        else:
            cargos = Cli068Cargo.objects.none()

        cargo_choices = [('', '----------')] + [(cargo.id, f"{cargo.nombre_cargo}") for cargo in cargos]
        
        self.fields['cargo'] = forms.ChoiceField(
            label='CARGO',
            choices=cargo_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccion una opción',
                }
            ),
            required=False
        )

        # Add other fields and their initialization logic here, similar to VacancyFormAll

        self.helper.layout = Layout(
            # 🏗️ DATOS GENERALES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Datos Principales</h4>"),
                    Div('titulo', css_class='col-12'),  # Título
                    Div('cargo', css_class='col-12'),  # Cargo
                    Div('numero_posiciones', css_class='col-4'),  # Número de vacantes
                    Div('cantidad_presentar', css_class='col-4'),  # Número a presentar
                    Div('fecha_presentacion', css_class='col-4'),  # Fecha de presentación
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💼 DETALLES DEL TRABAJO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Detalles del Trabajo</h4>"),
                    Div('termino_contrato', css_class='col-3'),  # Término de contrato
                    Div('tiempo_experiencia', css_class='col-3'),  # Tiempo de experiencia
                    Div('modalidad', css_class='col-3'),  # Modalidad
                    Div('jornada', css_class='col-3'),  # Jornada
                    Div('horario_inicio', css_class='col-3'),  # Horario
                    Div('horario_final', css_class='col-3'),  # Horario
                    Div('hora_inicio', css_class='col-3'),  # Horario
                    Div('hora_final', css_class='col-3'),  # Horario
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💼 LUGAR DEL TRABAJO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Lugar de Trabajo</h4>"),
                    Div('lugar_trabajo', css_class='col-6'),  # Lugar de trabajo
                    Div('barrio', css_class='col-6'),  # Barrio
                    Div('direccion', css_class='col-6'),  # Dirección
                    Div('url_mapa', css_class='col-6'),  # URL del mapa
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 🛠️ REQUISITOS Y HABILIDADES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Requisitos y Habilidades</h4>"),
                    Div('soft_skills', css_class='col-6'),  # Habilidades blandas
                    Div('hard_skills', css_class='col-6'),  # Habilidades duras
                    Div('idioma', css_class='col-6'),  # Idioma
                    Div('nivel_idioma', css_class='col-6'),  # nivel_idioma
                    Div('profesion_estudio', css_class='col-6'),  # Profesión o estudio
                    Div('nivel_estudio', css_class='col-4'),  # Nivel de estudio
                    Div('estado_estudio', css_class='col-2'),  # Estado de estudio
                    Div('edad_inicial', css_class='col-3'),  # Edad Inicial
                    Div('edad_final', css_class='col-3'),  # Edad Final
                    Div('genero', css_class='col-6'),  # genero
                    Div('estudios_complementarios', css_class='col-9'),  # estudios_complementarios
                    Div('estudios_complementarios_certificado', css_class='col-3'),  # estudios_complementarios_certificado
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💰 INFORMACIÓN SALARIAL
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Información Salarial</h4>"),
                    Div(
                        PrependedText('salario', '$', placeholder='0.00'),
                        css_class='col-6'
                    ),  # Salario
                    Div('tipo_salario', css_class='col-6'),  # Tipo de salario
                    Div('frecuencia_pago', css_class='col-6'),  # Frecuencia de pago
                    Div(
                        PrependedText('salario_adicional', '$', placeholder='0.00'),
                        css_class='col-6'
                    ),
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 📑 RESPONSABILIDADES DEL CARGO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Responsabilidades del Cargo</h4>"),
                    Div('funciones_responsabilidades', css_class='col-12'),  # Funciones y responsabilidades
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 🏗️ DESCRIPCION DE LA VACANTE
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Descripción de la Vacante</h4>"),
                    Div('descripcion_vacante', css_class='col-12'),  # Número de vacantes
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        # Validate titulo
        titulo = cleaned_data.get('titulo').upper() if cleaned_data.get('titulo') else ''
        
        if not titulo:
            self.add_error('titulo', 'El título es obligatorio.')
        elif len(titulo.split()) > 10:
            self.add_error('titulo', 'El título no puede exceder las 10 palabras.')

        #validate cargo
        cargo = cleaned_data.get('cargo')
        if not cargo:
            self.add_error('cargo', 'El cargo es obligatorio.')

        # Validate descripcion_vacante
        descripcion_vacante = cleaned_data.get('descripcion_vacante')
        if not descripcion_vacante:
            self.add_error('descripcion_vacante', 'La descripción de la vacante es obligatoria.')
        elif len(descripcion_vacante.split()) < 5:
            self.add_error('descripcion_vacante', 'La descripción de la vacante debe tener al menos 5 palabras.')

        # Validate funciones_responsabilidades
        funciones_responsabilidades = cleaned_data.get('funciones_responsabilidades')
        if not funciones_responsabilidades:
            self.add_error('funciones_responsabilidades', 'Las funciones y responsabilidades son obligatorias.')

        # Validate horario_inicio
        horario_inicio = cleaned_data.get('horario_inicio')
        if not horario_inicio:
            self.add_error('horario_inicio', 'El horario de inicio es obligatorio.')
        
        # Validate horario_final
        horario_final = cleaned_data.get('horario_final')
        if not horario_final:
            self.add_error('horario_final', 'El horario final es obligatorio.')
        
        # Validate hora_inicio
        hora_inicio = cleaned_data.get('hora_inicio')
        if not hora_inicio:
            self.add_error('hora_inicio', 'La hora de inicio es obligatoria.')
        
        # Validate hora_final
        hora_final = cleaned_data.get('hora_final')
        if not hora_final:
            self.add_error('hora_final', 'La hora final es obligatoria.')
        
        

        # Validate edad
        edad_inicial = cleaned_data.get('edad_inicial')
        edad_final = cleaned_data.get('edad_final')
        if not edad_inicial:
            self.add_error('edad_inicial', 'La edad inicial es obligatoria.')
        if not edad_final:
            self.add_error('edad_final', 'La edad final es obligatoria.')
        if edad_inicial and edad_final and int(edad_inicial) > int(edad_final):
            self.add_error('edad_final', 'La edad final debe ser mayor o igual a la edad inicial.')

        # Validate genero
        genero = cleaned_data.get('genero')
        if not genero:
            self.add_error('genero', 'El género es obligatorio.')

        # Validate tiempo_experiencia
        tiempo_experiencia = cleaned_data.get('tiempo_experiencia')
        if not tiempo_experiencia:
            self.add_error('tiempo_experiencia', 'El tiempo de experiencia es obligatorio.')

        # Validate modalidad
        modalidad = cleaned_data.get('modalidad')
        if not modalidad:
            self.add_error('modalidad', 'La modalidad es obligatoria.')

        # Validate jornada
        jornada = cleaned_data.get('jornada')
        if not jornada:
            self.add_error('jornada', 'La jornada es obligatoria.')

        # Validate salario
        salario = cleaned_data.get('salario')
        if salario:
            salario = salario.replace('.', '')
            salario = salario.replace(',', '.')
            print(salario)
            cleaned_data['salario'] = salario
        else:
            print('No hay salario')
            
        # Validate tipo_salario
        tipo_salario = cleaned_data.get('tipo_salario')
        if not tipo_salario:
            self.add_error('tipo_salario', 'El tipo de salario es obligatorio.')

        # Validate frecuencia_pago
        frecuencia_pago = cleaned_data.get('frecuencia_pago')
        if not frecuencia_pago:
            self.add_error('frecuencia_pago', 'La frecuencia de pago es obligatoria.')

        # Validate salario_adicional
        salario_adicional = cleaned_data.get('salario_adicional')
        if salario_adicional:
            # Eliminar puntos y signo $
            salario_adicional = str(salario_adicional).replace('.', '').replace('$', '').replace(' ', '')
            
            # Verificar si el salario adicional es un número válido
            if not salario_adicional.isdigit():
                self.add_error('salario_adicional', 'Ingrese un número válido para el salario adicional.')
            else:
                # Convertir el salario adicional a un decimal
                cleaned_data['salario_adicional'] = Decimal(salario_adicional)
        else:
            cleaned_data['salario_adicional'] = None
    
        # Validate idioma
        idioma = cleaned_data.get('idioma')
        if not idioma:
            self.add_error('idioma', 'El idioma es obligatorio.')

        # Validate nivel_idioma
        nivel_idioma = cleaned_data.get('nivel_idioma')
        if not nivel_idioma:
            self.add_error('nivel_idioma', 'El nivel de idioma es obligatorio.')

        # Validate profesion_estudio
        profesion_estudio = cleaned_data.get('profesion_estudio')
        if not profesion_estudio:
            self.add_error('profesion_estudio', 'La profesión o estudio es obligatorio.')

        # Validate nivel_estudio
        nivel_estudio = cleaned_data.get('nivel_estudio')
        if not nivel_estudio:
            self.add_error('nivel_estudio', 'El nivel de estudio es obligatorio.')

        # Validate lugar_trabajo
        lugar_trabajo = cleaned_data.get('lugar_trabajo')
        if not lugar_trabajo:
            self.add_error('lugar_trabajo', 'El lugar de trabajo es obligatorio.')

        # Validate termino_contrato
        termino_contrato = cleaned_data.get('termino_contrato')
        if not termino_contrato:
            self.add_error('termino_contrato', 'El término de contrato es obligatorio.')

        # Validate soft_skills
        soft_skills = cleaned_data.get('soft_skills')
        if not soft_skills:
            self.add_error('soft_skills', 'Las habilidades blandas son obligatorias.')

        # Validate hard_skills
        hard_skills = cleaned_data.get('hard_skills')
        if not hard_skills:
            self.add_error('hard_skills', 'Las habilidades duras son obligatorias.')

        # Validate estudios_complementarios
        estudios_complementarios = cleaned_data.get('estudios_complementarios')
        if estudios_complementarios and len(estudios_complementarios) > 255:
            self.add_error('estudios_complementarios', 'Los estudios complementarios no pueden exceder los 255 caracteres.')

        # Validate estudios_complementarios_certificado
        estudios_complementarios_certificado = cleaned_data.get('estudios_complementarios_certificado')
        if estudios_complementarios and estudios_complementarios_certificado is None:
            self.add_error('estudios_complementarios_certificado', 'Debe indicar si los estudios complementarios están certificados.')

        return cleaned_data
    

class VacancyAssingForm(forms.Form):

    
    def __init__(self, *args, cliente_id=None, **kwargs):
        super(VacancyAssingForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante_asignar'

        analistas = UsuarioBase.objects.filter(group=5, cliente_id_051=cliente_id).order_by('primer_apellido')
        analista_choices = [('', '----------')] + [(analista.id, f"{analista.primer_nombre} {analista.segundo_nombre} {analista.primer_apellido} {analista.segundo_apellido}") for analista in analistas]


        self.fields['analista_asignado'] = forms.ChoiceField(
            label='ANALISTA RESPONSABLE',
            choices=analista_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccione una opción',
                }
            ),
            required=True
        )

        self.helper.layout = Layout(
            # 🏗️ DATOS GENERALES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Datos Principales</h4>"),
                    Div('analista_asignado', css_class='col-12'),  # Título
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )


    def clean(self):
        cleaned_data = super().clean()

        # Validate analista_asignado
        analista_asignado = cleaned_data.get('analista_asignado')
        if not analista_asignado:
            self.add_error('analista_asignado', 'El analista asignado es obligatorio.')

        return cleaned_data

class VacancyAssignRecruiterForm(forms.Form):

    
    def __init__(self, *args, cliente_id=None, **kwargs):
        super(VacancyAssignRecruiterForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante_asignar'

        analistas = UsuarioBase.objects.filter(group=7, cliente_id_051=cliente_id).order_by('primer_apellido')
        analista_choices = [('', '----------')] + [(analista.id, f"{analista.primer_nombre} {analista.segundo_nombre} {analista.primer_apellido} {analista.segundo_apellido}") for analista in analistas]


        self.fields['reclutador_asignado'] = forms.ChoiceField(
            label='RECLUTADOR RESPONSABLE',
            choices=analista_choices,
            widget=forms.Select(
                attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccione una opción',
                }
            ),
            required=True
        )

        self.helper.layout = Layout(
            # 🏗️ DATOS GENERALES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Datos Principales</h4>"),
                    Div('reclutador_asignado', css_class='col-12'),  # Título
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )


    def clean(self):
        cleaned_data = super().clean()

        # Validate reclutador_asignado
        reclutador_asignado = cleaned_data.get('reclutador_asignado')
        if not reclutador_asignado:
            self.add_error('reclutador_asignado', 'El reclutador asignado es obligatorio.')

        return cleaned_data

class VacancyFormAllV2(forms.Form):
    
    titulo = forms.CharField(
        label='TITULO DE LA VACANTE',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
            }
        ),
        required=False
    )

    termino_contrato = forms.ChoiceField(
            label='Tipo de Contrato',
            choices=TERMINO_CONTRATO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-control text-dark ps-5 h-55',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)
    
    modalidad = forms.ChoiceField(
            label='Modalidad',
            choices=MODALIDAD_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)
    
    cantidad_presentar = forms.ChoiceField(
        label='Número de candidatos a presentar',
        choices=[('', '-->')] + [(i, str(i)) for i in range(1, 11)],
        widget=forms.Select(
            attrs={
                'class': 'form-control text-dark ps-5 h-55',
                'placeholder': '-->',
            }
        ),
        required=True
    )
    
    numero_posiciones = forms.ChoiceField(
        label="Número Vacantes",
        choices=[('', '-->')] + [(i, str(i)) for i in range(1, 11)],
        widget=forms.Select(
            attrs={
                'class': 'form-control text-dark ps-5 h-55',  # Clases CSS del campo
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
        ),
        required=True
    )

    fecha_presentacion = forms.DateField(
            label='Fecha de presentación de hoja de vida',
            widget=forms.DateInput(
            attrs= {
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la fecha de presentación',
                'type': 'date'
            }
            ),
            required=True
        )

    barrio = forms.CharField(
            label='Barrio',
            max_length=100,
            required=True,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese el barrio',
                }
            )
        )

    direccion = forms.CharField(
            label='Dirección',
            max_length=100,
            required=True,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese la dirección',
                }
            )
        )
    
    salario = forms.CharField(
            label='Salario',
            widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el salario',
                'x-data': '{}',
                'x-mask:dynamic': "$money($input, ',', '.', 0)",  # <-- sin decimales si no los necesitas
                'id': 'id_salario'
                }
            ), required=True)
    
    tipo_salario = forms.ChoiceField(
            label='Tipo de salario',
            choices=TIPO_SALARIO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)
    
    frecuencia_pago = forms.ChoiceField(
            label='Frecuencia de pago',
            choices=FRECUENCIA_PAGO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)

    salario_adicional = forms.DecimalField(
            label='Salario adicional',
            widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el salario adicional',
                'x-data': '{}',
                'x-mask:dynamic': "$money($input, ',', '.', 4)",  # <-- sin decimales si no los necesitas
                'id': 'id_salario_adicional'
            }
            ), required=False)
    
    edad_inicial = forms.ChoiceField(
            label='Edad mínima',
            choices=EDAD_SELECT_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)

    edad_final = forms.ChoiceField(
            label='Edad máxima',
            choices=EDAD_SELECT_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)

    genero = forms.ChoiceField(
            label='Genero',
            choices=GENERO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)

    
    
    motivo_vacante = forms.ChoiceField(
            label='Motivo de la vacante',
            choices=MOTIVO_VACANTE_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)
    
    otro_motivo = forms.CharField(
        label='Especifique el otro motivo',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el motivo',
        })
    )
    
    funciones_responsabilidades_1 = forms.CharField(
        label='Función y responsabilidad 1',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la primera función y responsabilidad',
            'rows': 2 # Ajusta las filas para que no sea tan grande
        })
    )
    funciones_responsabilidades_2 = forms.CharField(
        label='Función y responsabilidad 2',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la segunda función y responsabilidad',
            'rows': 2
        })
    )
    funciones_responsabilidades_3 = forms.CharField(
        label='Función y responsabilidad 3',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la tercera función y responsabilidad',
            'rows': 2
        })
    )



    skill_relacionales = forms.ModelMultipleChoiceField(
            queryset=Can104Skill.objects.filter(estado_id_004=1, grupo=1).order_by('id'),
            label='Relacionales',
            widget=forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input d-flex flex-wrap', # Clase para el input del checkbox
            }),
            required=False # Si quieres que la selección sea opcional
        )
        
    skill_personales = forms.ModelMultipleChoiceField(
            queryset=Can104Skill.objects.filter(estado_id_004=1, grupo=2).order_by('id'),
            label='Personales',
            to_field_name='id',
            widget=forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input d-flex flex-wrap', # Clase para el input del checkbox
            }),
            required=False # Si quieres que la selección sea opcional
        )

    skill_cognitivas = forms.ModelMultipleChoiceField(
            queryset=Can104Skill.objects.filter(estado_id_004=1, grupo=3).order_by('id'),
            label='Cognitivas',
            to_field_name='id',
            widget=forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input d-flex flex-wrap', # Clase para el input del checkbox
            }),
            required=False # Si quieres que la selección sea opcional
        )
        
    skill_digitales = forms.ModelMultipleChoiceField(
            queryset=Can104Skill.objects.filter(estado_id_004=1, grupo=4).order_by('id'),
            label='Liderazgo / Dirección',
            to_field_name='id',
            widget=forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input d-flex flex-wrap', # Clase para el input del checkbox
            }),
            required=False # Si quieres que la selección sea opcional
        )

    skill_liderazgo = forms.ModelMultipleChoiceField(
            queryset=Can104Skill.objects.filter(estado_id_004=1, grupo=5).order_by('id'),
            label='Digitales / Ágiles',
            to_field_name='id',
            widget=forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input d-flex flex-wrap', # Clase para el input del checkbox
            }),
            required=False # Si quieres que la selección sea opcional
        )
    
    grupo_fit_1 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=1).order_by('id'),
            label='Estilo trabajo predominante en el área:',
            to_field_name='id',
            widget=forms.RadioSelect(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )
    
    grupo_fit_2 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=2).order_by('id'),
            label='Tipo de liderazgo presente:',
            to_field_name='id',
            widget=forms.RadioSelect(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )
    
    grupo_fit_3 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=3).order_by('id'),
            label='Comunicación organizacional:',
            to_field_name='id',
            widget=forms.RadioSelect(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )

    grupo_fit_4 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=4).order_by('id'),
            label='Ritmo de trabajo:',
            to_field_name='id',
            widget=forms.RadioSelect(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )
    
    grupo_fit_5 = forms.ModelChoiceField(
            queryset=Cli077FitCultural.objects.filter(estado=1, grupo=5).order_by('id'),
            label='Estilo toma de decisiones:',
            to_field_name='id',
            widget=forms.RadioSelect(attrs={
                'class': 'form-check-input', # Clase para el input del radio
            }),
            required=False # Si quieres que la selección sea opcional
        )

    otro_motivador = forms.CharField(
        label='Otro motivador', 
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese otro motivador si aplica',
            }
        )
    )

    profesion_estudio = forms.ChoiceField(
        label='Profesión Específica',
        choices=[('', 'Seleccione una opción...')],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una profesión',
        }),
        required=False
    )

    tipo_profesion = forms.ChoiceField(
        label='Tipo de Selección de Profesión',
        choices= TIPO_PROFESION_CHOICES_STATIC,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione el tipo',
        }),
        required=True
    )

    grupo_profesion = forms.ChoiceField(
        label='Grupo de Profesiones',
        choices=[('', 'Seleccione una opción...')],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione un grupo',
        }),
        required=False
    )

    profesion_estudio_listado = forms.MultipleChoiceField(
        label='Listado Personalizado de Profesiones',
        choices=[],  # Se llena en __init__
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Busque y seleccione las profesiones...',
            'multiple': 'multiple',
            'style': 'width: 100%; min-height: 38px;'
        }),
        required=False
    )
    
    def __init__(self, *args, cliente_id=None, **kwargs):
        # Extraer initial antes de super() para validar fecha_presentacion en modo edición
        initial_data = kwargs.get('initial', {})

        super(VacancyFormAllV2, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante_cliente'

        # Fecha de presentación: no puede ser hoy ni fechas pasadas
        # En modo edición con fecha pasada, no establecer min para evitar error "not focusable"
        initial_fecha = initial_data.get('fecha_presentacion') if isinstance(initial_data, dict) else None
        if initial_fecha:
            try:
                from datetime import datetime
                fecha_val = datetime.strptime(str(initial_fecha)[:10], '%Y-%m-%d').date() if initial_fecha else None
                initial_fecha_pasada = fecha_val and fecha_val <= date.today()
            except (ValueError, TypeError):
                initial_fecha_pasada = False
        else:
            initial_fecha_pasada = False

        if not initial_fecha_pasada:
            fecha_minima = (date.today() + timedelta(days=1)).isoformat()
            self.fields['fecha_presentacion'].widget.attrs['min'] = fecha_minima

        if cliente_id:
            cargos = Cli068Cargo.objects.filter(cliente=cliente_id).order_by('nombre_cargo')
        else:
            cargos = Cli068Cargo.objects.none()

        cargo_choices = [('', '----------')] + [(cargo.id, f"{cargo.nombre_cargo}") for cargo in cargos]
        
        self.fields['cargo'] = forms.ChoiceField(
            label='Cargo',
            choices=cargo_choices,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-control text-dark ps-5 h-55',  # Clases CSS del campo  
            'data-control': 'select2',
            'data-placeholder': 'Seleccion una opción',
            }
        ), required=True)

        lugares_trabajo = Cat004Ciudad.objects.all().order_by('nombre')
        lugar_trabajo_choices = [('', '----------')] + [(lugar.id, f"{lugar.nombre}") for lugar in lugares_trabajo]

        self.fields['lugar_trabajo'] = forms.ChoiceField(
            label='Ciudad',
            choices=lugar_trabajo_choices,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)
        

        self.fields['tipo_horario'] = forms.ChoiceField(
            label='Tipo de horario',
            choices=TIPO_HORARIO_CHOICES_STATIC,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }),
            required=True
        )

        for i in range(1, 4):  # Para 3 bloques de horarios
            self.fields[f'horario_inicio_{i}'] = forms.ChoiceField(
                label=f'Día inicio {i}',
                choices=HORARIO_CHOICES_STATIC,
                widget=forms.Select(attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccione una opción',
                }),
                required=False
            )

            self.fields[f'horario_final_{i}'] = forms.ChoiceField(
                label=f'Día Final {i}',
                choices=HORARIO_CHOICES_STATIC,
                widget=forms.Select(attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccione una opción',
                }),
                required=False
            )

            self.fields[f'hora_inicio_{i}'] = forms.TimeField(
                label=f'Hora inicial {i}',
                widget=forms.TimeInput(attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese la hora de inicio',
                    'type': 'time',
                }),
                required=False
            )

            self.fields[f'hora_final_{i}'] = forms.TimeField(
                label=f'Hora final {i}',
                widget=forms.TimeInput(attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese la hora final',
                    'type': 'time',
                }),
                required=False
            )

        for i in range(1, 4):
            # Nombre único para cada campo, ej: 'tiempo_experiencia_1'
            field_name = f'tiempo_experiencia_{i}'
            is_required = (i == 1)  # Solo el primer bloque es obligatorio
            # Se añade el campo al diccionario de campos del formulario
            self.fields[field_name] = forms.ChoiceField(
                label=f'Tiempo de experiencia {i}', # Etiqueta dinámica
                choices=TIEMPO_EXPERIENCIA_CHOICES_STATIC,
                widget=forms.Select(attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccione una opción',
                }),
                required=is_required
            )   

            field_name = f'experiencia_especifica_en_{i}'
            self.fields[field_name] = forms.CharField(
                label=f'Experiencia específica en #{i}', # Etiqueta dinámica
                max_length=256,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Desarrollo de APIs con Django Rest Framework'
                }),
                required=is_required
            )

            for j in range(1, 3): # Crearemos hasta 2 pares de campos de idiomas
                # Nombres de campo para esta iteración
                idioma_field = f'idioma_{j}'
                nivel_field = f'nivel_idioma_{j}'

                # Crear y añadir el campo 'idioma'
                self.fields[idioma_field] = forms.ChoiceField(
                    label=f'Idioma {j}',
                    choices=IDIOMA_CHOICES_STATIC,
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    required=False
                )
                # Crear y añadir el campo 'nivel_idioma'
                self.fields[nivel_field] = forms.ChoiceField(
                    label='Nivel', # Un label más corto aquí se ve mejor
                    choices=NIVEL_IDIOMA_CHOICES_STATIC,
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    required=False
                )

        PROFESION_CHIOCE = [('', 'Seleccione una opción... ')] + [(profesion.id, profesion.nombre) for profesion in Cli055ProfesionEstudio.objects.all()]
        
        self.fields['profesion_estudio'] = forms.ChoiceField(
            label='Estudio o Profesión',
            choices=PROFESION_CHIOCE,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)
        
        self.fields['nivel_estudio'] = forms.ChoiceField(
            label='Nivel de estudio',
            choices=NIVEL_ESTUDIO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=True)
        
        self.fields['estado_estudio'] = forms.ChoiceField(
            label='¿Graduado?',
            choices=[(True, 'Sí'), (False, 'No')],
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ),
            required=False
        )
        
        self.fields['cantidad_semestres'] = forms.IntegerField(
            label='Semestres',
            widget=forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'max': '20',
                    'placeholder': ''
                }
            ),
            required=False,
            help_text='Solo se requiere si no está graduado'
        )
        
        for i in range(1, 4): # Bucle para crear 3 registros
            # Nombres de campo para esta iteración
            estudio_field = f'estudios_complementarios_{i}'
            certificado_field = f'estudios_complementarios_certificado_{i}'

            # Crear y añadir el campo de texto para el estudio
            self.fields[estudio_field] = forms.CharField(
                label=f'Estudio Complementario {i}',
                widget=forms.TextInput(attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ej: Curso de Marketing Digital, Diplomado en UX'
                }),
                required=False
            )
            # Crear y añadir el campo para el certificado
            self.fields[certificado_field] = forms.ChoiceField(
                label='Certificado',
                choices=[('', '¿Certificado?'), (True, 'Sí'), (False, 'No')],
                widget=forms.Select(attrs={
                    'class': 'form-select form-select-solid',
                }),
                required=False
            )

        motivadores = Cli078MotivadoresCandidato.objects.filter(estado=1).order_by('id')
        motivadores_choices = [(str(motivador.id), f"{motivador.nombre}") for motivador in motivadores]
        motivadores_titles = {str(m.id): (m.descripcion or m.nombre) for m in motivadores}
        self.motivadores_con_descripcion = [(str(m.id), m.nombre, m.descripcion or '') for m in motivadores]

        self.fields['motivadores_candidato'] = forms.MultipleChoiceField(
            label='Motivadores del candidato (máximo 2)',
            choices=motivadores_choices,
            widget=CheckboxSelectMultipleWithTitle(
                attrs={'class': 'form-check-input motivador-checkbox'},
                titles=motivadores_titles
            ),
            required=True,
            help_text='Puede seleccionar máximo 2 motivadores'
        )
        
        self.fields['comentarios'] = forms.CharField(
            label='Comentarios finales',
            widget=forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese la descripción de la vacante',
                    'rows': 5,
                    'cols': 30,
                    'id': 'id_comentarios'
                }
            ),
            required=True
        )

        self.fields['descripcion_vacante'] = forms.CharField(
            label='Descripción vacante',
            widget=forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ingrese la descripción de la vacante',
                    'rows': 5,
                    'cols': 30,
                    'id': 'id_descripcion_vacante'
                }
            ),
            required=True
        )

        # Cargar profesiones específicas
        profesiones = Cli055ProfesionEstudio.objects.filter(estado_id_001=1).order_by('nombre')
        profesion_choices = [('', 'Seleccione una opción...')] + [(p.id, p.nombre) for p in profesiones]
        self.fields['profesion_estudio'].choices = profesion_choices

        # Cargar listado de profesiones para Select2 múltiple
        profesion_listado_choices = [(str(p.id), p.nombre) for p in profesiones]
        self.fields['profesion_estudio_listado'].choices = profesion_listado_choices

        # Cargar grupos de profesiones
        grupos = Cli075GrupoProfesion.objects.filter(estado=1).order_by('nombre')
        grupo_choices = [('', 'Seleccione una opción...')] + [(g.id, g.nombre) for g in grupos]
        self.fields['grupo_profesion'].choices = grupo_choices

    def _validar_bloque_horario(self, cleaned_data, bloque_num, tipo_horario):
        """Valida que un bloque de horario esté completamente diligenciado"""
        dia_inicio = cleaned_data.get(f'horario_inicio_{bloque_num}')
        dia_final = cleaned_data.get(f'horario_final_{bloque_num}')
        hora_inicio = cleaned_data.get(f'hora_inicio_{bloque_num}')
        hora_final = cleaned_data.get(f'hora_final_{bloque_num}')

        # Verificar que todos los campos estén completos
        if not dia_inicio:
            self.add_error(f'horario_inicio_{bloque_num}', f'El día de inicio del bloque {bloque_num} es obligatorio para horario {tipo_horario}.')
        if not dia_final:
            self.add_error(f'horario_final_{bloque_num}', f'El día final del bloque {bloque_num} es obligatorio para horario {tipo_horario}.')
        if not hora_inicio:
            self.add_error(f'hora_inicio_{bloque_num}', f'La hora de inicio del bloque {bloque_num} es obligatoria para horario {tipo_horario}.')
        if not hora_final:
            self.add_error(f'hora_final_{bloque_num}', f'La hora final del bloque {bloque_num} es obligatoria para horario {tipo_horario}.')

        # Si todos están completos, validar lógica de horarios
        if all([dia_inicio, dia_final, hora_inicio, hora_final]):
            if dia_inicio == dia_final and hora_inicio >= hora_final:
                self.add_error(f'hora_final_{bloque_num}', f'La hora final debe ser mayor que la inicial en el bloque {bloque_num}.')

    def _validar_bloque_horario_opcional(self, cleaned_data, bloque_num, tipo_horario):
        """Valida un bloque de horario opcional - si se llena parcialmente, debe estar completo"""
        dia_inicio = cleaned_data.get(f'horario_inicio_{bloque_num}')
        dia_final = cleaned_data.get(f'horario_final_{bloque_num}')
        hora_inicio = cleaned_data.get(f'hora_inicio_{bloque_num}')
        hora_final = cleaned_data.get(f'hora_final_{bloque_num}')

        algun_dato = any([dia_inicio, dia_final, hora_inicio, hora_final])
        todos_diligenciados = all([dia_inicio, dia_final, hora_inicio, hora_final])

        if algun_dato and not todos_diligenciados:
            # Si se llenó alguno, pero no todos, marcar los que falten
            if not dia_inicio:
                self.add_error(f'horario_inicio_{bloque_num}', f'Debe completar este campo en el bloque de horario {bloque_num}')
            if not dia_final:
                self.add_error(f'horario_final_{bloque_num}', f'Debe completar este campo en el bloque de horario {bloque_num}')
            if not hora_inicio:
                self.add_error(f'hora_inicio_{bloque_num}', f'Debe completar este campo en el bloque de horario {bloque_num}')
            if not hora_final:
                self.add_error(f'hora_final_{bloque_num}', f'Debe completar este campo en el bloque de horario {bloque_num}')
        
        elif todos_diligenciados:
            # Si todos están diligenciados, validar que la hora final sea mayor
            if dia_inicio == dia_final and hora_inicio >= hora_final:
                self.add_error(f'hora_final_{bloque_num}', f'La hora final debe ser mayor que la inicial en el bloque {bloque_num}')

    def clean(self):
        cleaned_data = super().clean()
        
        #form data 1
        cargo = cleaned_data.get('cargo')
        if not cargo:
            self.add_error('cargo', 'El campo Cargo es obligatorio.')
        termino_contrato    = cleaned_data.get('termino_contrato')
        if not termino_contrato:
            self.add_error('termino_contrato', 'El campo Tipo de Contrato es obligatorio.')

        modalidad = cleaned_data.get('modalidad')
        if not modalidad:
            self.add_error('modalidad', 'El campo Modalidad es obligatorio.')

        cantidad_presentar = cleaned_data.get('cantidad_presentar')
        if not cantidad_presentar:
            self.add_error('cantidad_presentar', 'El campo Número de candidatos a presentar es obligatorio.')

        numero_posiciones = cleaned_data.get('numero_posiciones')
        if not numero_posiciones:
            self.add_error('numero_posiciones', 'El campo Número Vacantes es obligatorio.') 

        fecha_presentacion = cleaned_data.get('fecha_presentacion')
        if not fecha_presentacion:
            self.add_error('fecha_presentacion', 'El campo Fecha de presentación es obligatorio.')
        elif fecha_presentacion <= date.today():
            self.add_error('fecha_presentacion', 'La fecha de presentación debe ser posterior a la fecha actual.')
        lugar_trabajo = cleaned_data.get('lugar_trabajo')
        if not lugar_trabajo:
            self.add_error('lugar_trabajo', 'El campo Ciudad es obligatorio.')
        barrio = cleaned_data.get('barrio')
        if not barrio:
            self.add_error('barrio', 'El campo Barrio es obligatorio.')
        direccion = cleaned_data.get('direccion')
        if not direccion:
            self.add_error('direccion', 'El campo Dirección es obligatorio.')
        salario = cleaned_data.get('salario')
        if not salario:
            self.add_error('salario', 'El campo Salario es obligatorio.')
        tipo_salario = cleaned_data.get('tipo_salario')
        if not tipo_salario:
            self.add_error('tipo_salario', 'El campo Tipo de salario es obligatorio.')
        frecuencia_pago = cleaned_data.get('frecuencia_pago')
        if not frecuencia_pago:
            self.add_error('frecuencia_pago', 'El campo Frecuencia de pago es obligatorio.')
        salario_adicional = cleaned_data.get('salario_adicional')
        if salario_adicional is not None and salario_adicional < 0:
            self.add_error('salario_adicional', 'El campo Salario adicional no puede ser negativo.')
        edad_inicial = cleaned_data.get('edad_inicial')
        if not edad_inicial:
            self.add_error('edad_inicial', 'El campo Edad mínima es obligatorio.')
        edad_final = cleaned_data.get('edad_final')
        if not edad_final:
            self.add_error('edad_final', 'El campo Edad máxima es obligatorio.')
        if edad_inicial and edad_final and int(edad_inicial) > int(edad_final):
            self.add_error('edad_final', 'La edad final debe ser mayor o igual a la edad inicial.')
        genero = cleaned_data.get('genero')
        if not genero:  
            self.add_error('genero', 'El campo Género es obligatorio.')
        motivo_vacante = cleaned_data.get('motivo_vacante')
        if not motivo_vacante:
            self.add_error('motivo_vacante', 'El campo Motivo de la vacante es obligatorio.')
        if motivo_vacante == 'Otro':
            otro_motivo = cleaned_data.get('otro_motivo')
            if not otro_motivo:
                self.add_error('otro_motivo', 'El campo Otro motivo es obligatorio cuando se selecciona "Otro".')
        
        # Validación condicional de horarios según tipo_horario
        tipo_horario = cleaned_data.get('tipo_horario')
        if not tipo_horario or tipo_horario == '' or tipo_horario is None:
            self.add_error('tipo_horario', 'El campo Tipo de horario es obligatorio.')
        else:
            # Validar horarios según el tipo seleccionado
            if tipo_horario == 'HF':  # Horario Fijo - Solo Bloque 1 obligatorio
                self._validar_bloque_horario(cleaned_data, 1, 'HF')
            elif tipo_horario in ['HR', 'HX']:  # Horario Rotativo/Flexible - Bloques 1 y 2 obligatorios
                self._validar_bloque_horario(cleaned_data, 1, tipo_horario)
                self._validar_bloque_horario(cleaned_data, 2, tipo_horario)
                # Bloque 3 es opcional, pero si se llena debe estar completo
                self._validar_bloque_horario_opcional(cleaned_data, 3, tipo_horario)
        
        funciones_responsabilidades_1 = cleaned_data.get('funciones_responsabilidades_1')
        if not funciones_responsabilidades_1:
            self.add_error('funciones_responsabilidades_1', 'El campo Función y responsabilidad 1 es obligatorio.')
        
        #data 2
        for i in range(1, 4):
            tiempo_experiencia = cleaned_data.get(f'tiempo_experiencia_{i}')
            experiencia_especifica = cleaned_data.get(f'experiencia_especifica_en_{i}')

            if i == 1:
                # Primer bloque: ambos campos son obligatorios
                if not tiempo_experiencia:
                    self.add_error(f'tiempo_experiencia_{i}', 'Este campo es obligatorio.')
                if not experiencia_especifica:
                    self.add_error(f'experiencia_especifica_en_{i}', 'Este campo es obligatorio.')
            else:
                # Bloques 2 y 3: validación cruzada solo si uno está lleno
                if tiempo_experiencia and not experiencia_especifica:
                    self.add_error(f'experiencia_especifica_en_{i}', f'Debe ingresar la experiencia específica para el tiempo #{i}.')
                elif experiencia_especifica and not tiempo_experiencia:
                    self.add_error(f'tiempo_experiencia_{i}', f'Debe ingresar el tiempo de experiencia para el área #{i}.')

        for i in range(1, 3):  # Para 2 idiomas
            idioma = cleaned_data.get(f'idioma_{i}')
            nivel_idioma = cleaned_data.get(f'nivel_idioma_{i}')

            # Validación cruzada para ambos idiomas: si uno está lleno, el otro también debe estarlo
            if idioma and not nivel_idioma:
                self.add_error(f'nivel_idioma_{i}', f'Debe seleccionar el nivel para el idioma #{i}.')
            elif nivel_idioma and not idioma:
                self.add_error(f'idioma_{i}', f'Debe seleccionar el idioma #{i}.')
        
        
        
        nivel_estudio = cleaned_data.get('nivel_estudio')
        if not nivel_estudio:
            self.add_error('nivel_estudio', 'El campo NIVEL DE ESTUDIO es obligatorio.')
        
        for i in range(1, 4):
            estudio_complementario = cleaned_data.get(f'estudios_complementarios_{i}')
            certificado = cleaned_data.get(f'estudios_complementarios_certificado_{i}')

            if estudio_complementario and not certificado:
                self.add_error(f'estudios_complementarios_certificado_{i}', f'El campo Certificado es obligatorio si se ingresa un estudio complementario en el campo {i}.')
            elif not estudio_complementario and certificado:
                self.add_error(f'estudios_complementarios_{i}', f'El campo Estudio Complementario {i} es obligatorio si se selecciona un certificado.')

        # Validación de habilidades: máximo 2 por grupo
        grupos_skills = {
            'skill_relacionales': 'Habilidades Relacionales',
            'skill_personales': 'Habilidades Personales', 
            'skill_cognitivas': 'Habilidades Cognitivas',
            'skill_digitales': 'Habilidades Digitales',
            'skill_liderazgo': 'Habilidades de Liderazgo'
        }

        total_skills = 0
        grupos_con_errores = []

        for campo, nombre_grupo in grupos_skills.items():
            skills = cleaned_data.get(campo)
            if skills:
                cantidad_skills = len(skills)
                total_skills += cantidad_skills
                
                # Validar máximo 2 habilidades por grupo
                if cantidad_skills > 2:
                    grupos_con_errores.append(nombre_grupo)
                    self.add_error(campo, f'Puede seleccionar máximo 2 habilidades en {nombre_grupo}. Ha seleccionado {cantidad_skills}.')

        # Validar que haya al menos una habilidad seleccionada
        if total_skills < 1:
            raise forms.ValidationError("Debe seleccionar al menos una habilidad en total.")
        
        # Mostrar resumen de validación si hay errores
        if grupos_con_errores:
            grupos_texto = ", ".join(grupos_con_errores)
            raise forms.ValidationError(f"Error en los siguientes grupos: {grupos_texto}. Recuerde que puede seleccionar máximo 2 habilidades por grupo.")
        
        # Validación de Grupo Fit: al menos uno debe estar seleccionado
        grupos_fit_seleccionados = 0

        for i in range(1, 6):
            valor = cleaned_data.get(f'grupo_fit_{i}')
            if valor:
                grupos_fit_seleccionados += 1

        # Validar que haya al menos un Grupo Fit seleccionado
        if grupos_fit_seleccionados < 1:
            for i in range(1, 6):
                self.add_error(f'grupo_fit_{i}', 'Debe seleccionar al menos un Grupo Fit.')

        motivadores_candidato = cleaned_data.get('motivadores_candidato')
        if not motivadores_candidato:
            self.add_error('motivadores_candidato', 'El campo Motivadores del candidato es obligatorio.')
        elif len(motivadores_candidato) > 2:
            self.add_error('motivadores_candidato', 'Solo puede seleccionar máximo 2 motivadores.')
        descripcion_vacante = cleaned_data.get('descripcion_vacante')
        if not descripcion_vacante:
            self.add_error('descripcion_vacante', 'El campo Descripción vacante es obligatorio.')
        
        comentarios = cleaned_data.get('comentarios')
        if not comentarios:
            self.add_error('comentarios', 'El campo Comentarios finales es obligatorio.')
            if len(comentarios) > 50050:
                self.add_error('comentarios', 'El campo Comentarios finales no puede exceder los 500 caracteres.')
        
        descripcion_vacante = cleaned_data.get('descripcion_vacante')   
        if len(descripcion_vacante) > 10000:
            self.add_error('descripcion_vacante', 'El campo Descripción vacante no puede exceder los 500 caracteres.')

        tipo_profesion = cleaned_data.get('tipo_profesion')
        profesion_especifica = cleaned_data.get('profesion_estudio')
        grupo_profesion = cleaned_data.get('grupo_profesion')
        listado_profesion = cleaned_data.get('profesion_estudio_listado')
        profesion_estudio = cleaned_data.get('profesion_estudio')
        

        # Validación: solo una opción debe estar seleccionada
        campos_llenos = sum([
            bool(profesion_especifica),
            bool(grupo_profesion),
            bool(listado_profesion)
        ])

        if not tipo_profesion:
            self.add_error('tipo_profesion', 'Debe seleccionar un tipo de profesión.')
        elif tipo_profesion == 'E':
            if not profesion_especifica:
                self.add_error('profesion_estudio', 'Debe seleccionar una profesión específica.')
        elif tipo_profesion == 'G':
            if not grupo_profesion:
                self.add_error('grupo_profesion', 'Debe seleccionar un grupo de profesiones.')
        elif tipo_profesion == 'L':
            if not listado_profesion:
                self.add_error('profesion_estudio_listado', 'Debe ingresar al menos una profesión en el listado.')

        # Validación: solo una opción debe estar seleccionada
        if campos_llenos > 1:
            self.add_error(None, 'Solo puede seleccionar una opción: profesión específica, grupo de profesiones, o listado personalizado.')
        
        # Validación condicional para cantidad_semestres
        estado_estudio = cleaned_data.get('estado_estudio')
        cantidad_semestres = cleaned_data.get('cantidad_semestres')
        
        if estado_estudio == 'False' or estado_estudio is False:  # No graduado
            if not cantidad_semestres:
                self.add_error('cantidad_semestres', 'El campo Cantidad de semestres es obligatorio cuando no está graduado.')
            elif cantidad_semestres < 1 or cantidad_semestres > 20:
                self.add_error('cantidad_semestres', 'La cantidad de semestres debe estar entre 1 y 20.')

        # Convertir profesion_estudio_listado (lista de IDs) a JSON para almacenamiento
        listado_ids = cleaned_data.get('profesion_estudio_listado')
        if isinstance(listado_ids, list):
            if listado_ids:
                ids_int = [int(x) for x in listado_ids if str(x).isdigit()]
                profesiones_obj = Cli055ProfesionEstudio.objects.filter(id__in=ids_int)
                cleaned_data['profesion_estudio_listado'] = json.dumps([
                    {"value": p.nombre, "id": p.id} for p in profesiones_obj
                ])
            else:
                cleaned_data['profesion_estudio_listado'] = ""
        
        return cleaned_data