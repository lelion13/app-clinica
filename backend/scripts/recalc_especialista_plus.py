"""One-off: recalcular valor de asignaciones de módulo (plus especialista × servicio).

Por defecto es DRY-RUN (no escribe). Usar --apply para persistir.

Ejemplos (desde el container backend):

  python -m scripts.recalc_especialista_plus --periodo-id 3
  python -m scripts.recalc_especialista_plus --periodo-id 3 --ids 1706,1833 --apply

Regla (igual al alta):
  nuevo = catálogo × 1.20  si profesional.es_especialista AND servicio.especialista
  nuevo = catálogo         si no

Solo toca novedades_asignacion_modulo (deleted_at IS NULL). No toca novedades ni ajustes.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.novedades import (
    NovedadesAsignacionModulo,
    NovedadesModulo,
    NovedadesPeriodo,
    NovedadesProfesional,
    NovedadesServicio,
)
from app.services.novedades.prof_sync import modulo_valor_para_profesional


def _q(value: Decimal | None) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.01"))


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recalcular plus especialista en asignaciones de módulo de un período."
    )
    parser.add_argument("--periodo-id", type=int, required=True, help="ID de novedades_periodo")
    parser.add_argument(
        "--ids",
        type=str,
        default="",
        help="Opcional: IDs de asignación separados por coma (ej. 1706,1833). Solo esas filas.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persistir cambios. Sin este flag solo imprime el dry-run.",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="",
        help="Ruta opcional para guardar el detalle (dry-run o apply).",
    )
    return parser.parse_args(argv)


def _parse_ids(raw: str) -> set[int] | None:
    text = (raw or "").strip()
    if not text:
        return None
    out: set[int] = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        out.add(int(part))
    return out or None


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    only_ids = _parse_ids(args.ids)
    db = SessionLocal()
    try:
        periodo = db.execute(
            select(NovedadesPeriodo).where(
                NovedadesPeriodo.id == args.periodo_id,
                NovedadesPeriodo.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if not periodo:
            print(f"ERROR: período {args.periodo_id} no encontrado", file=sys.stderr)
            return 1

        servicios = {
            s.id: s
            for s in db.execute(
                select(NovedadesServicio).where(NovedadesServicio.deleted_at.is_(None))
            )
            .scalars()
            .all()
        }
        con_flag = sorted(s.nombre for s in servicios.values() if getattr(s, "especialista", False))
        print(
            f"Período #{periodo.id} · {periodo.nombre or 'sin nombre'} · "
            f"{periodo.fecha_inicio} → {periodo.fecha_fin} · estado={periodo.estado}"
        )
        print(
            f"Servicios con Especialista ON ({len(con_flag)}): "
            + (", ".join(con_flag) if con_flag else "(ninguno — el plus bajará a catálogo)")
        )
        if only_ids:
            print(f"Filtro --ids: {sorted(only_ids)}")
        if not con_flag:
            print(
                "AVISO: ningún servicio tiene especialista=true. "
                "Revisá Parametrización antes de --apply si esperabas mantener plus."
            )

        query = select(NovedadesAsignacionModulo).where(
            NovedadesAsignacionModulo.periodo_id == args.periodo_id,
            NovedadesAsignacionModulo.deleted_at.is_(None),
        )
        if only_ids is not None:
            query = query.where(NovedadesAsignacionModulo.id.in_(only_ids))
        asignaciones = list(db.execute(query).scalars().all())
        if only_ids is not None:
            found = {a.id for a in asignaciones}
            missing = sorted(only_ids - found)
            if missing:
                print(f"AVISO: IDs no encontrados en el período (o borrados): {missing}")
        if not asignaciones:
            print("Sin asignaciones activas en el período (con el filtro actual).")
            return 0

        modulos = {
            m.id: m
            for m in db.execute(select(NovedadesModulo).where(NovedadesModulo.deleted_at.is_(None)))
            .scalars()
            .all()
        }
        profesionales = {
            p.id: p
            for p in db.execute(
                select(NovedadesProfesional).where(NovedadesProfesional.deleted_at.is_(None))
            )
            .scalars()
            .all()
        }

        rows: list[dict] = []
        for item in asignaciones:
            modulo = modulos.get(item.modulo_id)
            servicio = servicios.get(item.servicio_id)
            professional = profesionales.get(item.professional_id)
            if not modulo or not servicio or not professional:
                rows.append(
                    {
                        "id": item.id,
                        "status": "SKIP_MISSING_REF",
                        "professional_id": item.professional_id,
                        "servicio_id": item.servicio_id,
                        "modulo_id": item.modulo_id,
                        "valor_actual": str(_q(item.valor)),
                        "valor_nuevo": "",
                        "delta": "",
                        "prof_especialista": "",
                        "servicio_especialista": "",
                        "catalogo": "",
                    }
                )
                continue

            catalog = _q(Decimal(modulo.valor))
            actual = _q(Decimal(item.valor))
            nuevo = _q(
                modulo_valor_para_profesional(
                    catalog,
                    es_especialista=bool(professional.es_especialista),
                    servicio_especialista=bool(getattr(servicio, "especialista", False)),
                )
            )
            delta = nuevo - actual
            status = "UNCHANGED" if delta == 0 else "CHANGE"
            rows.append(
                {
                    "id": item.id,
                    "status": status,
                    "legajo": professional.legajo or "",
                    "profesional": professional.full_name,
                    "servicio": servicio.nombre,
                    "modulo": modulo.descripcion,
                    "fecha_realizacion": str(item.fecha_realizacion),
                    "valor_actual": str(actual),
                    "valor_nuevo": str(nuevo),
                    "delta": str(delta),
                    "prof_especialista": str(bool(professional.es_especialista)),
                    "servicio_especialista": str(bool(getattr(servicio, "especialista", False))),
                    "catalogo": str(catalog),
                    "professional_id": item.professional_id,
                    "servicio_id": item.servicio_id,
                    "modulo_id": item.modulo_id,
                    "_item": item,
                    "_nuevo": nuevo,
                }
            )

        changes = [r for r in rows if r["status"] == "CHANGE"]
        skips = [r for r in rows if r["status"] == "SKIP_MISSING_REF"]
        unchanged = [r for r in rows if r["status"] == "UNCHANGED"]

        print(
            f"Asignaciones: {len(asignaciones)} · a cambiar: {len(changes)} · "
            f"iguales: {len(unchanged)} · skip: {len(skips)}"
        )
        if changes:
            print(
                f"{'id':>6}  {'legajo':8}  {'servicio':24}  {'actual':>12}  {'nuevo':>12}  {'delta':>12}  prof/svc"
            )
            for r in changes[:200]:
                print(
                    f"{r['id']:>6}  {str(r.get('legajo',''))[:8]:8}  {str(r.get('servicio',''))[:24]:24}  "
                    f"{r['valor_actual']:>12}  {r['valor_nuevo']:>12}  {r['delta']:>12}  "
                    f"{r['prof_especialista']}/{r['servicio_especialista']}"
                )
            if len(changes) > 200:
                print(f"… {len(changes) - 200} filas más (usar --csv para el detalle completo)")

        csv_path = (args.csv or "").strip()
        if csv_path:
            path = Path(csv_path)
            fieldnames = [
                "id",
                "status",
                "legajo",
                "profesional",
                "servicio",
                "modulo",
                "fecha_realizacion",
                "catalogo",
                "valor_actual",
                "valor_nuevo",
                "delta",
                "prof_especialista",
                "servicio_especialista",
                "professional_id",
                "servicio_id",
                "modulo_id",
            ]
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for r in rows:
                    writer.writerow(r)
            print(f"CSV escrito: {path.resolve()}")

        if not args.apply:
            print("DRY-RUN: no se escribió nada. Re-ejecutá con --apply para persistir.")
            return 0

        if not changes:
            print("Nada para aplicar.")
            return 0

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for r in changes:
            item = r["_item"]
            item.valor = r["_nuevo"]
            item.updated_at = now
        db.commit()
        print(f"APPLY OK: {len(changes)} asignación(es) actualizada(s).")
        return 0
    except Exception as exc:  # noqa: BLE001 — CLI surface
        db.rollback()
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
