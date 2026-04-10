import json
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required

from applications.usuarios.decorators import validar_permisos
from applications.common.models import Cat001Estado
from applications.cliente.models import (
    Cli085AccionesDecisivas,
    Cli067PoliticasInternas,
    Cli066PruebasPsicologicas,
)


def _json_error(message, status=400):
    return JsonResponse({"success": False, "message": message}, status=status)


def _get_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _estados_activo_inactivo():
    """Solo Activo e Inactivo (nombre exacto, sin distinguir mayúsculas)."""
    return Cat001Estado.objects.filter(
        Q(nombre__iexact="Activo") | Q(nombre__iexact="Inactivo")
    ).order_by("id")


def _estados_catalogo_dropdown(model_cls):
    """
    Opciones del select: Activo e Inactivo.
    Si hay filas con otro estado_id (histórico), se incluye ese id para poder editar.
    """
    base = _estados_activo_inactivo()
    allowed = set(base.values_list("pk", flat=True))
    if not allowed:
        return base
    legacy = set(
        model_cls.objects.exclude(estado_id__in=allowed).values_list(
            "estado_id", flat=True
        )
    )
    if not legacy:
        return base
    return Cat001Estado.objects.filter(Q(pk__in=allowed) | Q(pk__in=legacy)).order_by(
        "id"
    )


def _estado_debe_ser_activo_o_inactivo(estado):
    n = (estado.nombre or "").strip().lower()
    if n not in ("activo", "inactivo"):
        return _json_error("El estado debe ser Activo o Inactivo.")
    return None


# —— Decisiones definitivas (Cli085AccionesDecisivas) ——


@login_required
@validar_permisos("acceso_admin")
def config_decisiones(request):
    items = Cli085AccionesDecisivas.objects.select_related("estado").order_by("-id")
    estados = _estados_catalogo_dropdown(Cli085AccionesDecisivas)
    return render(
        request,
        "admin/config/catalog_decisiones.html",
        {"items": items, "estados": estados},
    )


@login_required
@validar_permisos("acceso_admin")
@require_http_methods(["GET"])
def api_decisiones_detail(request, pk):
    obj = get_object_or_404(Cli085AccionesDecisivas, pk=pk)
    jd = obj.json_data
    json_data_str = json.dumps(jd, ensure_ascii=False) if jd is not None else ""
    return JsonResponse(
        {
            "success": True,
            "item": {
                "id": obj.id,
                "nombre": obj.nombre,
                "descripcion": obj.descripcion or "",
                "cantidad_dias_gestion": obj.cantidad_dias_gestion,
                "estado_id": obj.estado_id,
                "fecha_cargue": obj.fecha_cargue.isoformat() if obj.fecha_cargue else None,
                "json_data": json_data_str,
            },
        }
    )


@login_required
@validar_permisos("acceso_admin")
@require_POST
def api_decisiones_guardar(request):
    data = _get_json_body(request)
    if data is None:
        return _json_error("JSON inválido")

    pk = data.get("id")
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        return _json_error("El nombre es obligatorio.")

    descripcion = (data.get("descripcion") or "").strip() or None
    estado_id = data.get("estado_id")
    if not estado_id:
        return _json_error("Debe seleccionar un estado.")
    estado = get_object_or_404(Cat001Estado, pk=estado_id)
    err_est = _estado_debe_ser_activo_o_inactivo(estado)
    if err_est:
        return err_est

    dias = data.get("cantidad_dias_gestion")
    if dias is not None and dias != "":
        try:
            dias = int(dias)
            if dias < 0:
                return _json_error("Los días de gestión no pueden ser negativos.")
        except (TypeError, ValueError):
            return _json_error("Días de gestión inválidos.")
    else:
        dias = None

    json_data_val = None
    raw_jd = data.get("json_data")
    if raw_jd is None:
        json_data_val = None
    elif isinstance(raw_jd, str):
        s = raw_jd.strip()
        if s:
            try:
                json_data_val = json.loads(s)
            except json.JSONDecodeError:
                return _json_error("El campo datos JSON no tiene un formato válido.")
        else:
            json_data_val = None
    else:
        # dict, list, int, float, bool, etc. enviados ya parseados en el cuerpo JSON
        json_data_val = raw_jd

    if pk:
        obj = get_object_or_404(Cli085AccionesDecisivas, pk=pk)
        obj.nombre = nombre
        obj.descripcion = descripcion
        obj.cantidad_dias_gestion = dias
        obj.estado = estado
        obj.json_data = json_data_val
        obj.save()
        msg = "Registro actualizado correctamente."
    else:
        Cli085AccionesDecisivas.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            cantidad_dias_gestion=dias,
            estado=estado,
            json_data=json_data_val,
        )
        msg = "Registro creado correctamente."

    return JsonResponse({"success": True, "message": msg})


# —— Políticas internas (Cli067PoliticasInternas) ——


@login_required
@validar_permisos("acceso_admin")
def config_politicas(request):
    items = Cli067PoliticasInternas.objects.select_related("estado").order_by("-id")
    estados = _estados_catalogo_dropdown(Cli067PoliticasInternas)
    return render(
        request,
        "admin/config/catalog_politicas.html",
        {"items": items, "estados": estados},
    )


@login_required
@validar_permisos("acceso_admin")
@require_http_methods(["GET"])
def api_politicas_detail(request, pk):
    obj = get_object_or_404(Cli067PoliticasInternas, pk=pk)
    rp = obj.respuestas_politica
    rp_str = json.dumps(rp, ensure_ascii=False) if rp is not None else ""
    return JsonResponse(
        {
            "success": True,
            "item": {
                "id": obj.id,
                "nombre": obj.nombre,
                "descripcion": obj.descripcion or "",
                "estado_id": obj.estado_id,
                "respuestas_politica": rp_str,
            },
        }
    )


@login_required
@validar_permisos("acceso_admin")
@require_POST
def api_politicas_guardar(request):
    data = _get_json_body(request)
    if data is None:
        return _json_error("JSON inválido")

    pk = data.get("id")
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        return _json_error("El nombre es obligatorio.")

    descripcion = (data.get("descripcion") or "").strip()
    if not descripcion:
        return _json_error("La descripción es obligatoria.")

    estado_id = data.get("estado_id")
    if not estado_id:
        return _json_error("Debe seleccionar un estado.")
    estado = get_object_or_404(Cat001Estado, pk=estado_id)
    err_est = _estado_debe_ser_activo_o_inactivo(estado)
    if err_est:
        return err_est

    raw_json = (data.get("respuestas_politica") or "").strip()
    respuestas = None
    if raw_json:
        try:
            respuestas = json.loads(raw_json)
        except json.JSONDecodeError:
            return _json_error("El campo respuestas (JSON) no es válido.")

    if pk:
        obj = get_object_or_404(Cli067PoliticasInternas, pk=pk)
        obj.nombre = nombre
        obj.descripcion = descripcion
        obj.estado = estado
        obj.respuestas_politica = respuestas
        obj.save()
        msg = "Registro actualizado correctamente."
    else:
        Cli067PoliticasInternas.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            estado=estado,
            respuestas_politica=respuestas,
        )
        msg = "Registro creado correctamente."

    return JsonResponse({"success": True, "message": msg})


# —— Pruebas psicológicas (Cli066PruebasPsicologicas) ——


@login_required
@validar_permisos("acceso_admin")
def config_pruebas(request):
    items = Cli066PruebasPsicologicas.objects.select_related("estado").order_by("-id")
    estados = _estados_catalogo_dropdown(Cli066PruebasPsicologicas)
    return render(
        request,
        "admin/config/catalog_pruebas.html",
        {"items": items, "estados": estados},
    )


@login_required
@validar_permisos("acceso_admin")
@require_http_methods(["GET"])
def api_pruebas_detail(request, pk):
    obj = get_object_or_404(Cli066PruebasPsicologicas, pk=pk)
    return JsonResponse(
        {
            "success": True,
            "item": {
                "id": obj.id,
                "nombre": obj.nombre,
                "descripcion": obj.descripcion or "",
                "uso": obj.uso or "",
                "cargos_recomendados": obj.cargos_recomendados or "",
                "estado_id": obj.estado_id,
            },
        }
    )


@login_required
@validar_permisos("acceso_admin")
@require_POST
def api_pruebas_guardar(request):
    data = _get_json_body(request)
    if data is None:
        return _json_error("JSON inválido")

    pk = data.get("id")
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        return _json_error("El nombre es obligatorio.")

    descripcion = (data.get("descripcion") or "").strip()
    if not descripcion:
        return _json_error("La descripción es obligatoria.")

    uso = (data.get("uso") or "").strip() or ""
    cargos_recomendados = (data.get("cargos_recomendados") or "").strip() or ""

    estado_id = data.get("estado_id")
    if not estado_id:
        return _json_error("Debe seleccionar un estado.")
    estado = get_object_or_404(Cat001Estado, pk=estado_id)
    err_est = _estado_debe_ser_activo_o_inactivo(estado)
    if err_est:
        return err_est

    if pk:
        obj = get_object_or_404(Cli066PruebasPsicologicas, pk=pk)
        obj.nombre = nombre
        obj.descripcion = descripcion
        obj.uso = uso
        obj.cargos_recomendados = cargos_recomendados
        obj.estado = estado
        obj.save()
        msg = "Registro actualizado correctamente."
    else:
        Cli066PruebasPsicologicas.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            uso=uso,
            cargos_recomendados=cargos_recomendados,
            estado=estado,
        )
        msg = "Registro creado correctamente."

    return JsonResponse({"success": True, "message": msg})
