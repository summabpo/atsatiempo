from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from applications.vacante.models import Cli052Vacante, Cli055ProfesionEstudio
from applications.common.models import Cat004Ciudad
from applications.cliente.models import Cli051Cliente
from applications.usuarios.models import UsuarioBase
from applications.vacante.models import Cli052Vacante

class VacanteForm(forms.Form):
    # EXPERIENCIA_TIEMPO = [
    #     ('', 'Seleccione una opción... '),
    #     (1, '0 a 6 Meses'),
    #     (2, '1 año a 2 años'),
    #     (3, 'Más de 2 años'),
    #     (4, 'Sin experiencia'),
    # ]

    EXPERIENCIA_TIEMPO = [('', 'Seleccione una opción... ')] + Cli052Vacante.EXPERIENCIA_TIEMPO

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
    experiencia_requerida = forms.ChoiceField(label='EXPERIENCIA ', choices = EXPERIENCIA_TIEMPO, widget = forms.Select( attrs={ 'class': 'form-select form-select-solid fw-bold'}), required=True)
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
        required=False
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
    # EXPERIENCIA_TIEMPO = [
    #     ('', 'Seleccione una opción... '),
    #     (1, '0 a 6 Meses'),
    #     (2, '1 año a 2 años'),
    #     (3, 'Más de 2 años'),
    #     (4, 'Sin experiencia'),
    # ]

    EXPERIENCIA_TIEMPO = [('', 'Seleccione una opción... ')] + Cli052Vacante.EXPERIENCIA_TIEMPO

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
    experiencia_requerida = forms.ChoiceField(label='EXPERIENCIA ', choices = EXPERIENCIA_TIEMPO, widget = forms.Select( attrs={ 'class': 'form-select form-select-solid fw-bold'}), required=True)
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
        required=False
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
    # EXPERIENCIA_TIEMPO = [
    #     ('', 'Seleccione una opción... '),
    #     (1, '0 a 6 Meses'),
    #     (2, '1 año a 2 años'),
    #     (3, 'Más de 2 años'),
    #     (4, 'Sin experiencia'),
    # ]

    EXPERIENCIA_TIEMPO = [('', 'Seleccione una opción... ')] + Cli052Vacante.EXPERIENCIA_TIEMPO

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
    experiencia_requerida = forms.ChoiceField(label='EXPERIENCIA ', choices = EXPERIENCIA_TIEMPO, widget = forms.Select( attrs={ 'class': 'form-select form-select-solid fw-bold'}), required=True)
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
        required=False
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