from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import NovedadesBonoOpcion, NovedadesProduccionTarifa
from app.schemas.novedades import (
    BonoOpcionResponse,
    ProduccionTarifaBulkCreateRequest,
    ProduccionTarifaCreateRequest,
    ProduccionTarifaResponse,
    ProduccionTarifaUpdateRequest,
)
from app.services.novedades.bonos_import import (
    INTERNACION_KEY,
    PRACTICA_KEY,
    opcion_key,
    opcion_label,
)

PRACTICA_OPCION = ("GLOBAL", "PRACTICA_TRAUMATOLOGICA", "—", "—")
INTERNACION_OPCION = ("GLOBAL", "INTERNACIONES", "—", "—")


def ensure_special_produccion_opciones(db: Session, actor_id: int | None = None) -> None:
    now = datetime.utcnow()
    for centro, servicio, semana, horario in (PRACTICA_OPCION, INTERNACION_OPCION):
        existing = db.execute(
            select(NovedadesBonoOpcion).where(
                NovedadesBonoOpcion.centro == centro,
                NovedadesBonoOpcion.servicio == servicio,
                NovedadesBonoOpcion.semana == semana,
                NovedadesBonoOpcion.horario == horario,
            )
        ).scalar_one_or_none()
        if not existing:
            db.add(
                NovedadesBonoOpcion(
                    centro=centro,
                    servicio=servicio,
                    semana=semana,
                    horario=horario,
                    created_at=now,
                    updated_at=now,
                    created_by=actor_id,
                    updated_by=actor_id,
                    deleted_at=None,
                )
            )
            db.commit()
        elif existing.deleted_at is not None:
            existing.deleted_at = None
            existing.updated_at = now
            if actor_id:
                existing.updated_by = actor_id
            db.commit()


def _opcion_response(opcion: NovedadesBonoOpcion) -> BonoOpcionResponse:
    key = opcion_key(opcion.centro, opcion.servicio, opcion.semana, opcion.horario)
    return BonoOpcionResponse(
        id=opcion.id,
        key=key,
        label=opcion_label(opcion.centro, opcion.servicio, opcion.semana, opcion.horario),
        centro=opcion.centro,
        servicio=opcion.servicio,
        semana=opcion.semana,
        horario=opcion.horario,
    )


def _tarifa_response(tarifa: NovedadesProduccionTarifa, opcion: NovedadesBonoOpcion) -> ProduccionTarifaResponse:
    base = _opcion_response(opcion)
    return ProduccionTarifaResponse(
        id=tarifa.id,
        opcion_id=tarifa.opcion_id,
        key=base.key,
        label=base.label,
        centro=base.centro,
        servicio=base.servicio,
        semana=base.semana,
        horario=base.horario,
        valor_unitario=int(tarifa.valor_unitario),
        created_at=tarifa.created_at,
        updated_at=tarifa.updated_at,
    )


def load_tarifas_by_opcion_key(db: Session) -> dict[str, int]:
    ensure_special_produccion_opciones(db)
    rows = list(
        db.execute(
            select(NovedadesProduccionTarifa, NovedadesBonoOpcion)
            .join(NovedadesBonoOpcion, NovedadesBonoOpcion.id == NovedadesProduccionTarifa.opcion_id)
            .where(
                NovedadesProduccionTarifa.deleted_at.is_(None),
                NovedadesBonoOpcion.deleted_at.is_(None),
            )
        ).all()
    )
    result: dict[str, int] = {}
    for tarifa, opcion in rows:
        key = opcion_key(opcion.centro, opcion.servicio, opcion.semana, opcion.horario)
        result[key] = int(tarifa.valor_unitario)
    return result


def valorize_bonos(bonos: dict[str, int] | None, tarifas: dict[str, int]) -> tuple[dict[str, int], int]:
    subtotales: dict[str, int] = {}
    total = 0
    for key, qty in (bonos or {}).items():
        subtotal = int(qty) * int(tarifas.get(key, 0))
        subtotales[key] = subtotal
        total += subtotal
    return subtotales, total


def valorize_practicas(
    practicas_list: list[dict],
    tarifas: dict[str, int],
) -> tuple[list[dict], int]:
    unit_tariff = int(tarifas.get(PRACTICA_KEY, 0))
    result = []
    total = 0
    for p in practicas_list:
        cant = int(p.get("cantidad", 0))
        subtotal = cant * unit_tariff
        total += subtotal
        result.append({
            "centro": p.get("centro", ""),
            "servicio": p.get("servicio", ""),
            "cantidad": cant,
            "valor_unitario": unit_tariff,
            "subtotal": subtotal,
        })
    return result, total


def valorize_internaciones(
    internaciones_list: list[dict],
    tarifas: dict[str, int],
) -> tuple[list[dict], int]:
    unit_tariff = int(tarifas.get(INTERNACION_KEY, 0))
    result = []
    total = 0
    for item in internaciones_list:
        cant = int(item.get("cantidad", 0))
        subtotal = cant * unit_tariff
        total += subtotal
        result.append({
            "sucursal": item.get("sucursal", ""),
            "cantidad": cant,
            "valor_unitario": unit_tariff,
            "subtotal": subtotal,
        })
    return result, total


def list_tarifas(db: Session) -> list[ProduccionTarifaResponse]:
    ensure_special_produccion_opciones(db)
    rows = list(
        db.execute(
            select(NovedadesProduccionTarifa, NovedadesBonoOpcion)
            .join(NovedadesBonoOpcion, NovedadesBonoOpcion.id == NovedadesProduccionTarifa.opcion_id)
            .where(NovedadesProduccionTarifa.deleted_at.is_(None))
            .order_by(
                NovedadesBonoOpcion.centro.asc(),
                NovedadesBonoOpcion.servicio.asc(),
                NovedadesBonoOpcion.semana.asc(),
                NovedadesBonoOpcion.horario.asc(),
            )
        ).all()
    )
    return [_tarifa_response(tarifa, opcion) for tarifa, opcion in rows]


def list_bono_opciones(db: Session, *, sin_tarifa: bool = False) -> list[BonoOpcionResponse]:
    ensure_special_produccion_opciones(db)
    opciones = list(
        db.execute(
            select(NovedadesBonoOpcion)
            .where(NovedadesBonoOpcion.deleted_at.is_(None))
            .order_by(
                NovedadesBonoOpcion.centro.asc(),
                NovedadesBonoOpcion.servicio.asc(),
                NovedadesBonoOpcion.semana.asc(),
                NovedadesBonoOpcion.horario.asc(),
            )
        )
        .scalars()
        .all()
    )
    if not sin_tarifa:
        return [_opcion_response(item) for item in opciones]

    tarifadas = set(
        db.execute(
            select(NovedadesProduccionTarifa.opcion_id).where(NovedadesProduccionTarifa.deleted_at.is_(None))
        )
        .scalars()
        .all()
    )
    return [_opcion_response(item) for item in opciones if item.id not in tarifadas]


def _get_opcion_or_404(db: Session, opcion_id: int) -> NovedadesBonoOpcion:
    opcion = db.execute(
        select(NovedadesBonoOpcion).where(
            NovedadesBonoOpcion.id == opcion_id,
            NovedadesBonoOpcion.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not opcion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opción de bono no encontrada")
    return opcion


def _tarifa_activa_for_opcion(db: Session, opcion_id: int) -> NovedadesProduccionTarifa | None:
    return db.execute(
        select(NovedadesProduccionTarifa).where(
            NovedadesProduccionTarifa.opcion_id == opcion_id,
            NovedadesProduccionTarifa.deleted_at.is_(None),
        )
    ).scalar_one_or_none()


def create_tarifa(
    db: Session, payload: ProduccionTarifaCreateRequest, actor_id: int
) -> ProduccionTarifaResponse:
    opcion = _get_opcion_or_404(db, payload.opcion_id)
    if _tarifa_activa_for_opcion(db, payload.opcion_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ya existe una tarifa para esa opción")
    now = datetime.utcnow()
    item = NovedadesProduccionTarifa(
        opcion_id=payload.opcion_id,
        valor_unitario=int(payload.valor_unitario),
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _tarifa_response(item, opcion)


def create_tarifas_bulk(
    db: Session, payload: ProduccionTarifaBulkCreateRequest, actor_id: int
) -> list[ProduccionTarifaResponse]:
    unique_ids = list(dict.fromkeys(payload.opcion_ids))
    if not unique_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Seleccioná al menos una opción")

    opciones: dict[int, NovedadesBonoOpcion] = {}
    for opcion_id in unique_ids:
        opcion = _get_opcion_or_404(db, opcion_id)
        if _tarifa_activa_for_opcion(db, opcion_id):
            label = opcion_label(opcion.centro, opcion.servicio, opcion.semana, opcion.horario)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Ya existe una tarifa para la opción {label}",
            )
        opciones[opcion_id] = opcion

    now = datetime.utcnow()
    created: list[ProduccionTarifaResponse] = []
    for opcion_id in unique_ids:
        opcion = opciones[opcion_id]
        item = NovedadesProduccionTarifa(
            opcion_id=opcion_id,
            valor_unitario=int(payload.valor_unitario),
            created_at=now,
            updated_at=now,
            created_by=actor_id,
            updated_by=actor_id,
            deleted_at=None,
        )
        db.add(item)
        db.flush()
        created.append(_tarifa_response(item, opcion))
    db.commit()
    return created


def update_tarifa(
    db: Session, tarifa_id: int, payload: ProduccionTarifaUpdateRequest, actor_id: int
) -> ProduccionTarifaResponse:
    row = db.execute(
        select(NovedadesProduccionTarifa, NovedadesBonoOpcion)
        .join(NovedadesBonoOpcion, NovedadesBonoOpcion.id == NovedadesProduccionTarifa.opcion_id)
        .where(
            NovedadesProduccionTarifa.id == tarifa_id,
            NovedadesProduccionTarifa.deleted_at.is_(None),
        )
    ).one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarifa no encontrada")
    tarifa, opcion = row
    tarifa.valor_unitario = int(payload.valor_unitario)
    tarifa.updated_at = datetime.utcnow()
    tarifa.updated_by = actor_id
    db.commit()
    db.refresh(tarifa)
    return _tarifa_response(tarifa, opcion)


def delete_tarifa(db: Session, tarifa_id: int, actor_id: int) -> None:
    tarifa = db.execute(
        select(NovedadesProduccionTarifa).where(
            NovedadesProduccionTarifa.id == tarifa_id,
            NovedadesProduccionTarifa.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not tarifa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarifa no encontrada")
    now = datetime.utcnow()
    tarifa.deleted_at = now
    tarifa.updated_at = now
    tarifa.updated_by = actor_id
    db.commit()
