from django import forms
from applications.services.choices import TIEMPO_EXPERIENCIA_CHOICES_STATIC
from applications.vacante.models import Cli052Vacante, Cli053SoftSkill, Cli054HardSkill, Cli055ProfesionEstudio, Cat004Ciudad, Cli073PerfilVacante
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from crispy_forms.layout import Div, HTML
from crispy_forms.bootstrap import PrependedText


class VacanteFiltro(forms.Form):
    

    salario_min = forms.CharField(
        label="Salario Minimo",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese salario mínimo'
        }),
        required=False
    )

    salario_max = forms.CharField(
        label="Salario Máximo",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Ingrese salario máximo'
        }),
        required=False
    )

    palabras_clave = forms.CharField(
        label="Palabras Clave",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Buscar por nombre del cargo, profesión, descripción...'
        }),
        required=False,
        help_text="Busca en el título, cargo, profesión y descripción de la vacante"
    )

    

    soft_skills = forms.ModelMultipleChoiceField(
        label='Habilidades Blandas',
        queryset=Cli053SoftSkill.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select form-select-lg form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione las habilidades',
            'data-allow-clear': 'true',
            'multiple': 'multiple'
        }),
        required=False
    )

    hard_skills = forms.ModelMultipleChoiceField(
        label='Habilidades Duras',
        queryset=Cli054HardSkill.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select form-select-lg form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Seleccione las habilidades',
            'data-allow-clear': 'true',
            'multiple': 'multiple'
        }),
        required=False
    )

    # hard_skills = forms.ModelMultipleChoiceField(
    #     label='HABILIDADES DURAS',
    #     queryset=Cli054HardSkill.objects.all(),
    #     widget=forms.CheckboxSelectMultiple(attrs={
    #         'class': 'form-check-input'
    #     }),
    #     required=False
    # )

    

    def __init__(self, *args, **kwargs):
        # Extraer datos del request para filtros dinámicos
        self.request_data = kwargs.pop('request_data', {})
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_filtros'
        self.helper.form_method = 'get'

        # Obtener filtros actuales
        ciudad_seleccionada = self.request_data.get('ciudad', '')
        experiencia_seleccionada = self.request_data.get('experiencia_requerida', '')
        profesion_seleccionada = self.request_data.get('profesion_estudio', '')
        palabras_clave = self.request_data.get('palabras_clave', '')

        # Construir queryset base
        queryset_base = Cli073PerfilVacante.objects.filter(
            estado=1,
            cli052vacante__estado_vacante__in=[1, 2]
        )

        # Aplicar filtros acumulativos para ciudades
        queryset_ciudades = queryset_base
        if profesion_seleccionada:
            if profesion_seleccionada.startswith('grupo_'):
                grupo_id = profesion_seleccionada.replace('grupo_', '')
                queryset_ciudades = queryset_ciudades.filter(grupo_profesion__id=grupo_id)
            else:
                from django.db.models import Q
                queryset_ciudades = queryset_ciudades.filter(
                    Q(profesion_estudio__id=profesion_seleccionada) |
                    Q(profesion_estudio_listado__icontains=f'"id":{profesion_seleccionada}')
                )
        if experiencia_seleccionada:
            experiencia_int = int(experiencia_seleccionada) if experiencia_seleccionada.isdigit() else None
            if experiencia_int:
                if experiencia_int == 6:  # Sin Experiencia
                    queryset_ciudades = queryset_ciudades.filter(tiempo_experiencia=6)
                else:
                    valores_experiencia = list(range(1, experiencia_int + 1))
                    queryset_ciudades = queryset_ciudades.filter(tiempo_experiencia__in=valores_experiencia)
        if palabras_clave:
            from django.db.models import Q
            queryset_ciudades = queryset_ciudades.filter(
                Q(cli052vacante__titulo__icontains=palabras_clave) |
                Q(cli052vacante__descripcion_vacante__icontains=palabras_clave) |
                Q(cli052vacante__cargo__nombre_cargo__icontains=palabras_clave) |
                Q(profesion_estudio__nombre__icontains=palabras_clave) |
                Q(grupo_profesion__nombre__icontains=palabras_clave) |
                Q(profesion_estudio_listado__icontains=palabras_clave)
            )

        ciudades_filtradas = queryset_ciudades.values_list(
            'lugar_trabajo__id',
            'lugar_trabajo__nombre'
        ).distinct().order_by('lugar_trabajo__nombre')

        ciudades_filtradas = [('', 'Seleccione una ciudad')] + list(ciudades_filtradas)

        # Campos del formulario
        self.fields['ciudad'] = forms.ChoiceField(
            label='Ciudad',
            choices=ciudades_filtradas,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Seleccione una opción',
            }),
            required=False
        )

        # Aplicar filtros acumulativos para experiencia
        queryset_experiencia = queryset_base
        if ciudad_seleccionada:
            queryset_experiencia = queryset_experiencia.filter(lugar_trabajo__id=ciudad_seleccionada)
        if profesion_seleccionada:
            if profesion_seleccionada.startswith('grupo_'):
                grupo_id = profesion_seleccionada.replace('grupo_', '')
                queryset_experiencia = queryset_experiencia.filter(grupo_profesion__id=grupo_id)
            else:
                from django.db.models import Q
                queryset_experiencia = queryset_experiencia.filter(
                    Q(profesion_estudio__id=profesion_seleccionada) |
                    Q(profesion_estudio_listado__icontains=f'"id":{profesion_seleccionada}')
                )
        if palabras_clave:
            from django.db.models import Q
            queryset_experiencia = queryset_experiencia.filter(
                Q(cli052vacante__titulo__icontains=palabras_clave) |
                Q(cli052vacante__descripcion_vacante__icontains=palabras_clave) |
                Q(cli052vacante__cargo__nombre_cargo__icontains=palabras_clave) |
                Q(profesion_estudio__nombre__icontains=palabras_clave) |
                Q(grupo_profesion__nombre__icontains=palabras_clave) |
                Q(profesion_estudio_listado__icontains=palabras_clave)
            )

        # Obtener los valores de experiencia disponibles
        experiencias_disponibles = queryset_experiencia.values_list(
            'tiempo_experiencia', flat=True
        ).distinct().order_by('tiempo_experiencia')

        # Crear opciones de experiencia basadas en las disponibles
        opciones_experiencia = [('', 'Seleccione una opción...')]
        for exp_id, exp_label in TIEMPO_EXPERIENCIA_CHOICES_STATIC[1:]:  # Excluir la opción vacía
            if exp_id in experiencias_disponibles:
                opciones_experiencia.append((exp_id, exp_label))

        self.fields['experiencia_requerida'] = forms.ChoiceField(
            label='Experiencia Requerida Mínima',
            choices=opciones_experiencia,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
            }),
            required=False
        )

        # Aplicar filtros acumulativos para profesiones
        queryset_profesiones = queryset_base
        if ciudad_seleccionada:
            queryset_profesiones = queryset_profesiones.filter(lugar_trabajo__id=ciudad_seleccionada)
        if experiencia_seleccionada:
            experiencia_int = int(experiencia_seleccionada) if experiencia_seleccionada.isdigit() else None
            if experiencia_int:
                if experiencia_int == 6:  # Sin Experiencia
                    queryset_profesiones = queryset_profesiones.filter(tiempo_experiencia=6)
                else:
                    valores_experiencia = list(range(1, experiencia_int + 1))
                    queryset_profesiones = queryset_profesiones.filter(tiempo_experiencia__in=valores_experiencia)
        if palabras_clave:
            from django.db.models import Q
            queryset_profesiones = queryset_profesiones.filter(
                Q(cli052vacante__titulo__icontains=palabras_clave) |
                Q(cli052vacante__descripcion_vacante__icontains=palabras_clave) |
                Q(cli052vacante__cargo__nombre_cargo__icontains=palabras_clave) |
                Q(profesion_estudio__nombre__icontains=palabras_clave) |
                Q(grupo_profesion__nombre__icontains=palabras_clave) |
                Q(profesion_estudio_listado__icontains=palabras_clave)
            )

        # Obtener profesiones de diferentes fuentes
        profesiones_set = set()
        
        # 1. Profesiones individuales (profesion_estudio)
        profesiones_individuales = queryset_profesiones.filter(
            profesion_estudio__isnull=False
        ).values_list('profesion_estudio__id', 'profesion_estudio__nombre').distinct()
        
        for prof_id, prof_nombre in profesiones_individuales:
            if prof_id and prof_nombre:
                profesiones_set.add((prof_id, prof_nombre))
        
        # 2. Grupos de profesiones (grupo_profesion)
        grupos_profesiones = queryset_profesiones.filter(
            grupo_profesion__isnull=False
        ).values_list('grupo_profesion__id', 'grupo_profesion__nombre').distinct()
        
        for grupo_id, grupo_nombre in grupos_profesiones:
            if grupo_id and grupo_nombre:
                profesiones_set.add((f"grupo_{grupo_id}", grupo_nombre))
        
        # 3. Profesiones del listado JSON (profesion_estudio_listado)
        import json
        for perfil in queryset_profesiones.filter(profesion_estudio_listado__isnull=False):
            try:
                if perfil.profesion_estudio_listado:
                    profesiones_json = json.loads(perfil.profesion_estudio_listado)
                    if isinstance(profesiones_json, list):
                        for prof in profesiones_json:
                            if isinstance(prof, dict) and 'id' in prof and 'value' in prof:
                                profesiones_set.add((prof['id'], prof['value']))
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Convertir a lista ordenada
        profesiones_lista = sorted(list(profesiones_set), key=lambda x: x[1])
        profesion_estudio_opciones = [('', 'Seleccione una Profesión o Estudio')] + profesiones_lista

        self.fields['profesion_estudio'] = forms.ChoiceField(
            label='Profesión o Estudio',
            choices=profesion_estudio_opciones,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-solid',  # Clases CSS del campo  
                'data-control': 'select2',
                'data-placeholder': 'Seleccion una opción',
            }),
            required=False
        )

        self.helper.layout = Layout(
            #  DATOS GENERALES
            Div(
            Div(
                HTML("<h5 class='mb-3 text-primary'>Buscar por:</h5>"),
                Div('palabras_clave', css_class='col-md-12 mb-3'),  # Palabras clave
                Div('ciudad', css_class='col-md-4'),             # ciudad
                Div('profesion_estudio', css_class='col-md-4'),  # profesion_estudio
                Div('experiencia_requerida', css_class='col-md-4'),  # Experiencvia Requerida
                # Div('salario_min', css_class='col-md-6'),        # Salario Minimo
                # Div('salario_max', css_class='col-md-6'),        # Salario Maximo
                css_class='row'
            ),
            css_class="mb-4 p-3 border rounded bg-primary bg-opacity-10"
            ),
        )