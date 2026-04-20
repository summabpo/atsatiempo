"""Acciones decisivas activas y sincronización Cli086 (cargo ↔ acción decisiva)."""

from applications.cliente.models import (
    Cli085AccionesDecisivas,
    Cli086AsignacionCargoAccionesDecisivas,
)
from applications.common.models import Cat001Estado


def acciones_decisivas_activas():
    return Cli085AccionesDecisivas.objects.filter(
        estado__nombre__iexact="Activo"
    ).select_related("estado").order_by("nombre")


def parse_acciones_seleccion_post(post):
    selected = set()
    for key in post:
        if not key.startswith("accion_"):
            continue
        try:
            aid = int(key.split("_", 1)[1])
        except (ValueError, IndexError):
            continue
        if post.get(key):
            selected.add(aid)
    return selected


def sync_cli086_solo_relacion(cargo, selected_ids):
    activos = set(acciones_decisivas_activas().values_list("pk", flat=True))
    selected_ids = {i for i in selected_ids if i in activos}

    estado_def = Cat001Estado.objects.filter(pk=1).first()

    Cli086AsignacionCargoAccionesDecisivas.objects.filter(cargo=cargo).exclude(
        accion_decisiva_id__in=selected_ids
    ).delete()

    for aid in selected_ids:
        acc = Cli085AccionesDecisivas.objects.filter(pk=aid).first()
        if not acc:
            continue
        Cli086AsignacionCargoAccionesDecisivas.objects.get_or_create(
            cargo=cargo,
            accion_decisiva_id=aid,
            defaults={"estado": estado_def or acc.estado},
        )


def acciones_cargo_ui_rows(cargo):
    asig_ids = set(
        Cli086AsignacionCargoAccionesDecisivas.objects.filter(cargo=cargo).values_list(
            "accion_decisiva_id", flat=True
        )
    )
    rows = []
    for a in acciones_decisivas_activas():
        rows.append({"accion": a, "checked": a.id in asig_ids})
    return rows


def acciones_decisivas_asignadas_cargo_activas(cargo):
    """
    Acciones decisivas activas vinculadas al cargo (Cli086), para UI (p. ej. modal de gestión).
    Devuelve lista de dicts serializables a JSON.
    """
    if cargo is None:
        return []
    rows = (
        Cli086AsignacionCargoAccionesDecisivas.objects.filter(cargo=cargo)
        .select_related("accion_decisiva", "accion_decisiva__estado")
        .order_by("accion_decisiva__nombre")
    )
    out = []
    for row in rows:
        acc = row.accion_decisiva
        est = getattr(acc, "estado", None)
        if est and (est.nombre or "").strip().lower() != "activo":
            continue
        out.append(
            {
                "id": acc.id,
                "nombre": acc.nombre,
                "descripcion": (acc.descripcion or "").strip(),
                "json_data": acc.json_data,
                "cantidad_dias_gestion": acc.cantidad_dias_gestion,
            }
        )
    return out
