import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Row, Column, Fieldset

from applications.services.service_vacanty import get_vacanty_questions

class PreguntasReclutamiento(forms.Form):
    """
    Formulario dinámico para preguntas de reclutamiento generadas a partir de get_vacanty_questions.
    Cada pregunta es de tipo Sí/No (BooleanField).
    """

    def __init__(self, vacante_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        preguntas = get_vacanty_questions(vacante_id)
        print("--------------------------------")
        print(preguntas)
        print("--------------------------------")
        
        # Configurar el helper una sola vez
        self.helper = FormHelper()
        self.helper.form_id = 'form-preguntas-reclutamiento'
        self.helper.form_tag = True
        
        choices = [('', 'Seleccione una opción')] + [('si', 'Sí'), ('no', 'No')]
        
        if preguntas:
            layout_fields = []
            
            for idx, pregunta in enumerate(preguntas):
                field_name = pregunta.get("pregunta", f"pregunta_{idx}")
                self.fields[field_name] = forms.ChoiceField(
                    label=pregunta.get("pregunta", f" Pregunta {idx+1}"),
                    choices=choices,
                    widget=forms.Select(attrs={
                        'class': 'form-select form-select-solid',
                        'data-control': 'select2',
                        'data-placeholder': 'Seleccione una opción',
                    }),
                    required=True
                )
                
                # Guardar metadatos
                self.fields[field_name].pregunta_tipo = pregunta.get("tipo_pregunta")
                self.fields[field_name].bloque = pregunta.get("bloque")
                self.fields[field_name].valores_relacionados = pregunta.get("valores_relacionados", None)
                
                # Agregar al layout
                layout_fields.append(
                    Div(
                        Div(field_name, css_class='col-md-12'),
                        css_class='row mb-4'
                    )
                )
            
            # Definir el layout completo
            self.helper.layout = Layout(*layout_fields)

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.fields:
            value = cleaned_data.get(field_name)
            if value in [None, '', 'Seleccione una opción']:
                self.add_error(field_name, "Debe seleccionar una opción para esta pregunta.")
        return cleaned_data
