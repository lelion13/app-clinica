# Design: limpiar-ui-obsoleta

## Safety rule

Antes de borrar cualquier módulo/endpoint/tabla: `rg` / búsqueda en FE+BE. Si aparece fuera de las tres features → **no borrar**.

## Frontend

1. `DISTRIBUTION_ITEMS`: quitar las 3 entradas.
2. `main.jsx`: quitar imports/rutas; añadir `<Navigate to="/" replace />` (o equivalente) para los 3 paths.
3. Borrar `WeeklyOccupancyPage.jsx`, `AgendaPage.jsx`, `EstadisticasPage.jsx` (+ CSS/helpers solo suyos si existen).
4. Verificar Home / otros links no referencian esos paths.

## Backend removal candidates (verify then delete)

| Módulo | Prefijo | Tabla(s) | Nota |
|--------|---------|----------|------|
| bookings | `/api/v1/bookings` | `bookings` | Solo AgendaPage |
| weekly_assignments | `/api/v1/weekly-assignments` | `room_weekly_assignments` | WeeklyOccupancy + stats |
| stats | `/api/v1/stats` | — (sin tabla propia) | Solo EstadisticasPage; lee weekly + hours |

**No eliminar:** `professionals`, `consulting_rooms`, `room_operating_hours`, `locations`, todo `distribucion/ocupacion/*`.

Pasos BE:
1. Quitar `include_router` en `main.py`.
2. Borrar routers/services/schemas/models (+ exports `__init__`, `alembic/env.py`).
3. Borrar/ajustar tests dedicados.
4. Migración: `DROP TABLE` bookings y room_weekly_assignments (orden por FKs).

## Spec sync

- REMOVED: Menú Estadística; API e UI Estadística.
- MODIFIED: Menú Ocupación (sin exigir Ocupación semanal); UI Agenda ocupación (sin “`/agenda` intacta”); Indicadores (sin coexistir con Estadística); Traceability.

## Verify matrix (smoke)

| Pantalla | Check |
|----------|-------|
| Home | Carga |
| Ocupación | Sync/list |
| Agenda ocupación | Events + DnD |
| Indicadores | KPIs |
| Profesionales | List/sync |
| Consultorios | Grilla + Agendas |
| URLs viejas | → Home |
