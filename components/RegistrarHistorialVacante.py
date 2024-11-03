from django.shortcuts import render, redirect, get_object_or_404

#utils
from django.utils.timezone import now

#modelos
from applications.vacante.models import Cli063AplicacionVacanteHistorial, Cli056AplicacionVacante
from applications.usuarios.models import UsuarioBase

# components
from components.RegistrarGestionVacante import validar_vacante_cierre

def crear_historial_aplicacion(aplicacion_vacante, estado, usuario=None, descripcion=None):
    
    usuario = get_object_or_404(UsuarioBase, id=usuario)

    # Trae el nombre del estado.
    estado_actual = obtener_nombre_estado_aplicacion(aplicacion_vacante.estado_aplicacion)

    # # Trae el nombre del estado.
    # diccionario_estados = dict(Cli056AplicacionVacante.ESTADO_APLICACION)
    # estado_actual = diccionario_estados.get(estado, "Estado no válido")

    # Trae el nombre del estado.
    estado_nuevo = obtener_nombre_estado_aplicacion(estado)
    descripcion = f'{descripcion}, Cambio de estado de {estado_actual} a {estado_nuevo}'

    # crea el registro del historial
    historial = Cli063AplicacionVacanteHistorial.objects.create(
        aplicacion_vacante_056=aplicacion_vacante,
        fecha=now(),  # Usamos now() en lugar de auto_now_add para más control.
        usuario_id_genero=usuario,
        estado=estado,
        descripcion=descripcion
    )

    aplicacion_vacante.estado_aplicacion = estado
    aplicacion_vacante.fecha_actualizacion = now()
    aplicacion_vacante.save()

    if validar_vacante_cierre(vacante_id=aplicacion_vacante.vacante_id_052.id) == True:
        # crea el registro del historial
        historial = Cli063AplicacionVacanteHistorial.objects.create(
            aplicacion_vacante_056=aplicacion_vacante,
            fecha=now(),  # Usamos now() en lugar de auto_now_add para más control.
            usuario_id_genero=usuario,
            estado=estado,
            descripcion= 'Vacante Cerrada'
        )

    return historial

def obtener_nombre_estado_aplicacion(estado):
    # Trae el nombre del estado.
    diccionario_estados = dict(Cli056AplicacionVacante.ESTADO_APLICACION)
    nombre_estadp = diccionario_estados.get(estado, "Estado no válido")

    return nombre_estadp