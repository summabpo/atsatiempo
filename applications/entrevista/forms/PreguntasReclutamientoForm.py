import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Layout, Div, Submit, HTML, Row, Column, Fieldset

from applications.services.service_vacanty import get_vacanty_questions

# INSERT_YOUR_CODE

class PreguntasReclutamiento(forms.Form):
    """
    Formulario dinámico para preguntas de reclutamiento generadas a partir de get_vacanty_questions.
    Cada pregunta es de tipo Sí/No (BooleanField).
    """



    def __init__(self, vacante_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        preguntas = get_vacanty_questions(vacante_id)
        if preguntas:
            for idx, pregunta in enumerate(preguntas):
                field_name = f"pregunta_{idx}"
                self.fields[field_name] = forms.ChoiceField(
                    label=pregunta.get("pregunta", f"Pregunta {idx+1}"),
                    choices=[('si', 'Sí'), ('no', 'No')],
                    widget=forms.RadioSelect,
                    required=True
                )
                # Puedes guardar metadatos si lo necesitas
                self.fields[field_name].pregunta_tipo = pregunta.get("tipo_pregunta")
                self.fields[field_name].bloque = pregunta.get("bloque")
                self.fields[field_name].valores_relacionados = pregunta.get("valores_relacionados", None)
    
                # INSERT_YOUR_CODE
            # Definir el layout dinámicamente para mostrar cada pregunta y su campo de respuesta en una fila
            self.helper = FormHelper()
            self.helper.form_tag = True
            layout_fields = []
            for idx, pregunta in enumerate(preguntas):
                field_name = f"pregunta_{idx}"
                layout_fields.append(
                    Row(
                        Column(
                            HTML(f"<label class='form-label fw-semibold'>{pregunta.get('pregunta', f'Pregunta {idx+1}')}</label>"),
                            css_class="col-12 col-md-8 mb-2"
                        ),
                        Column(
                            Fieldset(
                                "",
                                field_name,
                                css_class="mb-0"
                            ),
                            css_class="col-12 col-md-4 mb-2 d-flex align-items-center"
                        ),
                        css_class="mb-3 align-items-center"
                    )
                )
            self.helper.layout = Layout(*layout_fields)
