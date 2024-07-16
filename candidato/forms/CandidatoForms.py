import re, os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from common.models import Cat001Estado, Cat004Ciudad
from ..models import Can101Candidato, Can102Experiencia, Can103Educacion, Can104Skill 

