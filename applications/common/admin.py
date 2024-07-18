from django.contrib import admin
from .models import Cat001Estado, Cat004Ciudad
# Register your models here.

class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'sigla')
    short_description = "Estado"
admin.site.register(Cat001Estado, EstadoAdmin)

class CiudadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    short_description = "Estado"
admin.site.register(Cat004Ciudad, CiudadAdmin)