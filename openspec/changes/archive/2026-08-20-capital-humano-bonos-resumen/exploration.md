# Exploration: capital-humano-bonos-resumen

## Topic

Importar desde producción el resumen de bonos (`/bonos/resumen`) hacia Capital Humano: columnas dinámicas por opción, persistidas por período, con congelación al cerrar período.

## Current State

- Capital Humano: 1 fila/profesional (legajo, cargas, ajustes, total) + Detalle + 2 XLS; roles admin/rrhh.
- Período: `fecha_inicio` / `fecha_fin` / `estado` open|closed.
- Sync externos: backend `httpx` + Bearer `NOVEDADES_PROF_SYNC_TOKEN`.

## Affected Areas

- `backend/app/services/novedades/` — import bonos + merge en Capital Humano
- `backend/app/api/routers/novedades.py` — POST import + GET solo-bonos + export XLS con bonos
- `backend/app/models/novedades.py` + Alembic — persistencia snapshot
- `backend/app/core/config.py` — URL resumen (+ reutilizar token)
- `frontend/.../NovedadesXlsPage.jsx` — botón, columnas, modal solo-bonos, 3er XLS
- `docs/runbook.md`

## Approaches

1. **Snapshot por período (elegido)** — tabla(s) de cantidades; import reemplaza si período open; grilla lee DB.
2. **Solo sesión** — descartado (Q3=B).

## Recommendation

Proxy backend; match CODPROF; columnas `centro|servicio|semana|horario`; persistir; solo-bonos en modal; 3er XLS; freeze al cerrar período; XLS siempre descargable en este change (pruebas).

## Risks

- CODPROF mismatch / ceros
- Muchas columnas dinámicas (UI horizontal scroll)
- API lento/TLS :8001
- Re-import con período cerrado mal validado

## Ready for Proposal

Yes — survey Q1–Q10 cerrada en `decisions.md`.
