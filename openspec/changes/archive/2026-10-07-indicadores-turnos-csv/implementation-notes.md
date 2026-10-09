# Implementation notes — indicadores-turnos-csv

Entregado 2026-10-05 → cerrado/archivado **2026-10-07**. Branch de trabajo: `agenda-ocupacion-dnd`.

## Comportamiento

- Botón **Importar datos de turnos** en `/indicadores-ocupacion`.
- CSV formato ejemplo (`ID Persona`, `Estado Turno`, `Nombre`, fechas…).
- Persistencia: `turnos_csv_import` + `turnos_csv_row` (filename + período min/max `Fecha Turno`); varios imports coexisten.
- Match exacto normalizado `Nombre` ↔ `nombre_agenda` sync; unmatched → 422 + modal filas.
- KPIs bajo torta: turnos AT+AU, ausentes AU, % ausentismo, avg min presente→atendido (AT), avg días espera (AT). Filtran por Día|Mes UI + ubicación/consultorio/especialidad/médico vía agenda sistema.

## Ops / incidente 413

CSV ~7.9MB → nginx default 1m → **413**. Fix: `client_max_body_size 32m` en `frontend/nginx.conf` (+ mensaje UI). Requiere redeploy imagen frontend. Validado en prod por usuario (2026-10-07).

## Archivos

- `backend/alembic/versions/0030_turnos_csv.py`
- `backend/app/models/turnos_csv.py`
- `backend/app/services/distribucion/turnos_csv.py`
- `backend/app/api/routers/distribucion.py`
- `frontend/src/pages/IndicadoresOcupacionPage.jsx`
- `frontend/nginx.conf`, `frontend/src/services/api.js`
- `docs/runbook.md`

## Tests / smoke

- `pytest tests/test_turnos_csv.py` → **4 passed**
- Smoke: import CSV OK tras deploy nginx 32m
