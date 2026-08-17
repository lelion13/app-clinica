# Design: novedades-modulos-edicion

## Data

`novedades_modulo.produccion` BOOLEAN NOT NULL DEFAULT false  
Alembic: `0018_modulo_produccion` (revises `0017_sin_prod_motivo`).

## API

| Method | Path | Body |
|--------|------|------|
| POST | `/modulos` | + `produccion` (default false); `servicio_ids` min 1 |
| PUT | `/modulos/{id}` | `descripcion`, `comentario`, `valor`, `produccion` — **no** servicios |
| PUT | `/modulos/{id}/servicios` | `{ "servicio_ids": number[] }` — allow `[]` |
| DELETE | `/modulos/{id}` | soft-delete (sin cambio de contrato; UI confirma antes) |
| GET | `/modulos` | response includes `produccion` |

Auth writes: `require_admin_or_rrhh`.

Service layer: `update_modulo` no llama `_set_modulo_servicios`; `update_modulo_servicios` usa `_validate_servicio_ids(..., allow_empty=True)`.

## UI Param (`NovedadesParamPage` tab Módulos)

| Acción | UI |
|--------|-----|
| Lista | Solo grilla + botón **Nuevo módulo** (sin form inline) |
| Alta | Modal: mismos campos que el form viejo; **Cancelar** / **Cargar** |
| Editar | Botón `editar` → modal Guardar/Cancelar |
| Servicios | Botón `servicios` → modal Aceptar/Cancelar (0 ok) |
| Eliminar | Botón `eliminar` → modal confirmación con datos; **Cancelar** / **Eliminar**; Esc = cancelar |
| Lista | Sin badge `produccion` (Q8=B) |

Esc cierra el modal activo (create / edit / servicios / delete) si no hay save en curso.

## Carga (`NovedadesCargaPage`)

Antes del create submit:
- Si hay `moduloId` y ese módulo tiene `produccion === false` → **no** llamar `checkTieneProduccion` (ni exigir CODPROF para ese path)
- Si solo novedad, o módulo con `produccion=true` → check + force modal si false (change `novedades-tiene-produccion`)
- Editar fecha: siempre check (sin skip por flag del módulo de la fila)

## Files

- `backend/alembic/versions/0018_modulo_produccion.py`
- `backend/app/models/novedades.py`, `schemas/novedades.py`
- `backend/app/services/novedades/masters.py`
- `backend/app/api/routers/novedades.py`
- `backend/tests/test_novedades_modulos_edicion.py`
- `frontend/src/pages/novedades/NovedadesParamPage.jsx`
- `frontend/src/pages/novedades/NovedadesCargaPage.jsx`
- `docs/runbook.md`

## Tests

`test_novedades_modulos_edicion.py`: default `produccion=false`, update sin tocar servicios, servicios `[]`, 404.
