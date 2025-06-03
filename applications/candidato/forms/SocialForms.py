from applications.candidato.models import Can105RedSocial
from applications.common.models import Cat001Estado
from crispy_forms.helper import FormHelper
from django import forms
from crispy_forms.layout import Layout, Div, Submit

class SocialNetworkForm(forms.Form):
    red_social_id_105 = forms.ModelChoiceField(
        queryset=Can105RedSocial.objects.all(),
        label="Red Social",
        required=True,
        # Define los atributos comunes aquí.
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-control': 'select2',
        })
    )
    url = forms.URLField(
        max_length=255,
        label="URL del Perfil",
        required=False
    )
    

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(SocialNetworkForm, self).__init__(*args, **kwargs)

        # if not self.instance:
        #     self.fields['red_social_id_105'].widget.attrs['data-dropdown-parent'] = '#redes_candidato'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'

        self.helper.layout = Layout(
            Div(
                Div(
                    Div('red_social_id_105', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('url', css_class='col'),
                    css_class='row'
                ),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        red_social_id_105 = cleaned_data.get('red_social_id_105')
        url = cleaned_data.get('url')  

        if not red_social_id_105:
            self.add_error('red_social_id_105', 'Debe seleccionar una red social.')

        if url:
            if not url.startswith('http://') and not url.startswith('https://'):
                self.add_error('url', 'La URL debe comenzar con http:// o https://')
        else:
            self.add_error('url', 'Debe ingresar la URL del perfil.')


        return cleaned_data