from django.contrib import admin
from .models import Can101Candidato, Can102Experiencia, Can103Educacion, Can104Skill
# Register your models here.
admin.site.register(Can101Candidato)
admin.site.register(Can102Experiencia)
admin.site.register(Can103Educacion)
admin.site.register(Can104Skill)