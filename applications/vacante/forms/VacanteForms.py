from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Div, HTML
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio
from applications.common.models import Cat004Ciudad
from applications.cliente.models import Cli051Cliente, Cli068Cargo
from applications.usuarios.models import UsuarioBase
from applications.vacante.models import Cli052Vacante

#choices
from applications.services.choices import TIPO_CLIENTE_STATIC, EDAD_CHOICES_STATIC, GENERO_CHOICES_STATIC, TIEMPO_EXPERIENCIA_CHOICES_STATIC, MODALIDAD_CHOICES_STATIC, JORNADA_CHOICES_STATIC, TIPO_SALARIO_CHOICES_STATIC, FRECUENCIA_PAGO_CHOICES_STATIC, NIVEL_ESTUDIO_CHOICES_STATIC, TERMINO_CONTRATO_CHOICES_STATIC, HORARIO_CHOICES_STATIC

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
    numero_posiciones = forms.IntegerField(label="NUMERO VACANTES",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',  # Clases CSS del campo  
            }
        ), required=False)
    
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

        

        self.fields['edad'] = forms.ChoiceField(
            label='EDAD',
            choices=EDAD_CHOICES_STATIC,
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

        self.fields['horario'] = forms.CharField(
            widget=forms.TextInput(attrs={
            'id': 'id_horario',  # ID personalizado para que el JS lo seleccione
            'class': 'tagify--custom-dropdown', 
            'placeholder': 'Por favor ingrese los días del horario de trabajo ',
            }),
            required=True
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

        self.fields['salario'] = forms.DecimalField(
            label='SALARIO',
            widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el salario',
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
            widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el salario adicional',
            }
            ), required=False)

        self.fields['idioma'] = forms.CharField(
            label='IDIOMA',
            widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese el idioma',
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

        self.fields['lugar_trabajo'] = forms.ModelChoiceField(
            label='LUGAR DE TRABAJO',
            queryset=Cat004Ciudad.objects.all(),
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
        
        self.helper.layout = Layout(
            # 🏗️ DATOS GENERALES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Datos Principales</h4>"),
                    Div('titulo', css_class='col-12'),  # Título
                    Div('cargo', css_class='col-6'),  # Cargo
                    Div('numero_posiciones', css_class='col-6'),  # Número de vacantes
                    Div('descripcion_vacante', css_class='col-12'),  # Número de vacantes
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💼 DETALLES DEL TRABAJO
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Detalles del Trabajo</h4>"),
                    Div('termino_contrato', css_class='col-6'),  # Término de contrato
                    Div('lugar_trabajo', css_class='col-6'),  # Lugar de trabajo
                    Div('tiempo_experiencia', css_class='col-4'),  # Tiempo de experiencia
                    Div('modalidad', css_class='col-4'),  # Modalidad
                    Div('jornada', css_class='col-4'),  # Jornada
                    Div('horario', css_class='col-12'),  # Horario
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
                    Div('profesion_estudio', css_class='col-6'),  # Profesión o estudio
                    Div('nivel_estudio', css_class='col-6'),  # Nivel de estudio
                    Div('edad', css_class='col-6'),  # Edad
                    Div('genero', css_class='col-6'),  # genero
                    css_class='row'
                ),
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),

            # 💰 INFORMACIÓN SALARIAL
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Información Salarial</h4>"),
                    Div('salario', css_class='col-6'),  # Salario
                    Div('tipo_salario', css_class='col-6'),  # Tipo de salario
                    Div('frecuencia_pago', css_class='col-6'),  # Frecuencia de pago
                    Div('salario_adicional', css_class='col-6'),  # Salario adicional
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
        )

        
    def clean(self):
        cleaned_data = super().clean()
        # Validate titulo
        titulo = cleaned_data.get('titulo')
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

        # Validate horario
        horario = cleaned_data.get('horario')
        if not horario:
            self.add_error('horario', 'El horario es obligatorio.')

        
        # Validate tipo_cliente
        tipo_cliente = cleaned_data.get('tipo_cliente')

        # Validate edad
        edad = cleaned_data.get('edad')

        # Validate genero
        genero = cleaned_data.get('genero')

        # Validate tiempo_experiencia
        tiempo_experiencia = cleaned_data.get('tiempo_experiencia')

        # Validate modalidad
        modalidad = cleaned_data.get('modalidad')

        # Validate jornada
        jornada = cleaned_data.get('jornada')

        # Validate salario
        salario = cleaned_data.get('salario')

        # Validate tipo_salario
        tipo_salario = cleaned_data.get('tipo_salario')

        # Validate frecuencia_pago
        frecuencia_pago = cleaned_data.get('frecuencia_pago')

        # Validate salario_adicional
        salario_adicional = cleaned_data.get('salario_adicional')

        # Validate idioma
        idioma = cleaned_data.get('idioma')

        # Validate profesion_estudio
        profesion_estudio = cleaned_data.get('profesion_estudio')

        # Validate nivel_estudio
        nivel_estudio = cleaned_data.get('nivel_estudio')

        # Validate lugar_trabajo
        lugar_trabajo = cleaned_data.get('lugar_trabajo')

        # Validate termino_contrato
        termino_contrato = cleaned_data.get('termino_contrato')

        # Validate soft_skills
        soft_skills = cleaned_data.get('soft_skills')

        # Validate hard_skills
        hard_skills = cleaned_data.get('hard_skills')

        return cleaned_data