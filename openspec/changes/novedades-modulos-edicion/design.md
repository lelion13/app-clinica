# Design: novedades-modulos-edicion

## Data

`novedades_modulo.produccion` BOOLEAN NOT NULL DEFAULT false (Alembic `0018_modulo_produccion`, revises `0017_sin_prod_motivo`).

## API

| Method | Path | Body |
|--------|------|------|
| POST | `/modulos` | + `produccion` (default false); `servicio_ids` min 1 |
| PUT | `/modulos/{id}` | `descripcion`, `comentario`, `valor`, `produccion` — **no** servicios |
| PUT | `/modulos/{id}/servicios` | `{ "servicio_ids": number[] }` — allow `[]` |
| GET | `/modulos` | response includes `produccion` |

Auth: `require_admin_or_rrhh` for writes.

## UI Param

- Create: checkbox “Producción” + servicios ≥1
- Row: `editar` → modal Guardar/Cancelar; `servicios` → modal Aceptar/Cancelar (0 ok)
- Lista: sin badge producción

## Carga

Before create submit:
- If `moduloId` selected and that módulo `produccion === false` → skip `checkTieneProduccion`
- Else (solo novedad, o módulo con `produccion=true`) → check as today (force modal if false)
- Edit fecha: always check (unchanged)

## Files

- `0018_modulo_produccion.py`, models, schemas, `masters.py`, router
- `NovedadesParamPage.jsx`, `NovedadesCargaPage.jsx`
- tests + runbook
