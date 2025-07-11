from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Div, HTML, Field
from applications.candidato.models import Can104Skill
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio
from applications.common.models import Cat004Ciudad
from applications.cliente.models import Cli051Cliente, Cli068Cargo
from applications.usuarios.models import UsuarioBase
from applications.vacante.models import Cli052Vacante
from crispy_forms.bootstrap import PrependedText
from decimal import Decimal

#choices
from applications.services.choices import EDAD_SELECT_CHOICES_STATIC, IDIOMA_CHOICES_STATIC, NIVEL_CHOICHES_STATIC, NIVEL_IDIOMA_CHOICES_STATIC, TIPO_CLIENTE_STATIC, EDAD_CHOICES_STATIC, GENERO_CHOICES_STATIC, TIEMPO_EXPERIENCIA_CHOICES_STATIC, MODALIDAD_CHOICES_STATIC, JORNADA_CHOICES_STATIC, TIPO_SALARIO_CHOICES_STATIC, FRECUENCIA_PAGO_CHOICES_STATIC, NIVEL_ESTUDIO_CHOICES_STATIC, TERMINO_CONTRATO_CHOICES_STATIC, HORARIO_CHOICES_STATIC, MOTIVO_VACANTE_CHOICES_STATIC

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

        analistas = UsuarioBase.objects.filter(group__id=6).order_by('primer_apellido')
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
            ), required=False)
    
    modalidad = forms.ChoiceField(
            label='Modalidad',
            choices=MODALIDAD_CHOICES_STATIC,
            widget=forms.Select(
            
            ), required=False)
    
    cantidad_presentar = forms.ChoiceField(
        label='Número de candidatos a presentar',
        choices=[('', '-->')] + [(i, str(i)) for i in range(1, 11)],
        widget=forms.Select(
            attrs={
                'class': 'form-control text-dark ps-5 h-55',
                'placeholder': '-->',
            }
        ),
        required=False
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
        required=False
    )

    fecha_presentacion = forms.DateField(
            label='Fecha de presentación',
            widget=forms.DateInput(
            attrs= {
                'class': 'form-control form-control-solid',
                'placeholder': 'Ingrese la fecha de presentación',
                'type': 'date'
            }
            ),
            required=False
        )

    barrio = forms.CharField(
            label='Barrio',
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
            label='Dirección',
            max_length=100,
            required=False,
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
            ), required=False)
    
    tipo_salario = forms.ChoiceField(
            label='Tipo de salario',
            choices=TIPO_SALARIO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)
    
    frecuencia_pago = forms.ChoiceField(
            label='Frecuencia de pago',
            choices=FRECUENCIA_PAGO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

    salario_adicional = forms.DecimalField(
            label='Salación adicional',
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
            ), required=False)

    edad_final = forms.ChoiceField(
            label='Edad máxima',
            choices=EDAD_SELECT_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)

    genero = forms.ChoiceField(
            label='Genero',
            choices=GENERO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)
    
    motivo_vacante = forms.ChoiceField(
            label='Motivo de la vacante',
            choices=MOTIVO_VACANTE_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)
    
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
        required=False,
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


    
    def __init__(self, *args, cliente_id=None, **kwargs):
        super(VacancyFormAllV2, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacante_cliente'

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
        ), required=False)

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
            ), required=False)
        

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
                label=f'Gora final {i}',
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
            
            # Se añade el campo al diccionario de campos del formulario
            self.fields[field_name] = forms.ChoiceField(
                label=f'Tiempo de experiencia {i}', # Etiqueta dinámica
                choices=TIEMPO_EXPERIENCIA_CHOICES_STATIC,
                widget=forms.Select(attrs={
                    'class': 'form-select form-select-solid',
                    'data-control': 'select2',
                    'data-placeholder': 'Seleccione una opción',
                }),
                required=False
            )   

            field_name = f'experiencia_especifica_en_{i}'
            self.fields[field_name] = forms.CharField(
                label=f'Experiencia específica en #{i}', # Etiqueta dinámica
                max_length=256,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Desarrollo de APIs con Django Rest Framework'
                }),
                required=False
            )

            for i in range(1, 3): # Crearemos hasta 3 pares de campos
                # Nombres de campo para esta iteración
                idioma_field = f'idioma_{i}'
                nivel_field = f'nivel_idioma_{i}'

                # Crear y añadir el campo 'idioma'
                self.fields[idioma_field] = forms.ChoiceField(
                    label=f'Idioma {i}',
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
            label='NIVEL DE ESTUDIO',
            choices=NIVEL_ESTUDIO_CHOICES_STATIC,
            widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }
            ), required=False)
        
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

        self.helper.layout = Layout(
            # 1  DATOS GENERALES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Información general del cargo</h4>"),
                    HTML("<p class='mb-3 text-primary'>Ingresa </p>"),
                    Div('cargo', css_class='col-md-12'),
                    Div('termino_contrato', css_class='col-md-2'),
                    Div('modalidad', css_class='col-md-2'),
                    Div('numero_posiciones', css_class='col-md-2'),
                    Div('cantidad_presentar', css_class='col-md-3'),
                    Div('fecha_presentacion', css_class='col-md-2'),
                    css_class='row'
                ),
                # Más campos aquí...
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10 tab-pane fade show active",
                css_id="pane-data1",
                role="tabpanel",
                aria_labelledby="tab-data1",
                tabindex="0"
            ),

            # 2 REQUISITOS DEL TECNICOS  / HARD SKILLS
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Información general del cargo</h4>"),
                    HTML("<p class='mb-3 text-primary'>Lo que el cargo necesita para operar eficientemente </p>"),
                    
                    css_class='row'
                ),
                # Más campos aquí...
                css_class="tab-pane fade",
                css_id="pane-data2",
                role="tabpanel",
                aria_labelledby="tab-data2",
                tabindex="0"
            ),

            # 3 HABLIDADES BLANDAS  / SOFT SKILLS
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Sof Skills</h4>"),
                    HTML("<p class='mb-3 text-primary'>Lo que el cargo necesita para operar eficientemente </p>"),
                    
                    css_class='row'
                ),
                # Más campos aquí...
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10 tab-pane fade",
                css_id="pane-data3",
                role="tabpanel",
                aria_labelledby="tab-data3",
                tabindex="0"
            ),

            # 4 FIT CULTURAL
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Fit Cultural</h4>"),
                    HTML("<p class='mb-3 text-primary'>Lo que el cargo necesita para operar eficientemente </p>"),
                    
                    css_class='row'
                ),
                # Más campos aquí...
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10 tab-pane fade",
                css_id="pane-data4",
                role="tabpanel",
                aria_labelledby="tab-data4",
                tabindex="0"
            ),

            # 5 MOTIVADORES
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Motivadore</h4>"),
                    HTML("<p class='mb-3 text-primary'>Lo que el cargo necesita para operar eficientemente </p>"),
                    
                    css_class='row'
                ),
                # Más campos aquí...
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10 tab-pane fade",
                css_id="pane-data5",
                role="tabpanel",
                aria_labelledby="tab-data5",
                tabindex="0"
            ),

            # 6 COMENTARIOS
            Div(
                Div(
                    HTML("<h4 class='mb-3 text-primary'>Competencia</h4>"),
                    HTML("<p class='mb-3 text-primary'>Lo que el cargo necesita para operar eficientemente </p>"),
                    
                    css_class='row'
                ),
                # Más campos aquí...
                css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10 tab-pane fade",
                css_id="pane-data6",
                role="tabpanel",
                aria_labelledby="tab-data6",
                tabindex="0"
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

        
    
