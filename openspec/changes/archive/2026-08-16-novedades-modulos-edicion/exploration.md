# Exploration: novedades-modulos-edicion

## Topic

En Parametrización → Módulos: (1) editar datos del módulo vía modal + atributo booleano `produccion`; (2) asociar/desasociar uno o más servicios vía modal aparte.

## Current State

- UI: `NovedadesParamPage.jsx` tab Módulos — create (descripcion, comentario, valor, checkboxes servicios), list, delete. **Sin** botones editar ni asociar.
- Backend ya tiene `PUT /novedades/modulos/{id}` con `descripcion`, `comentario`, `valor`, `servicio_ids` (min 1) → `update_modulo` + `_set_modulo_servicios` (soft-delete M2M).
- Modelo `novedades_modulo`: sin columna `produccion`.
- M2M: `novedades_modulo_servicio` (activo = `deleted_at IS NULL`).
- Roles: create/update/delete = admin/rrhh; list = novedades reader.
- OpenSpec archivado: `2026-07-29-novedades-modulos`. Relacionado activo: `novedades-tiene-produccion` (carga, no master).

## Affected Areas

- `backend/app/models/novedades.py` — columna `produccion`
- Alembic nueva rev
- `backend/app/schemas/novedades.py` — create/update/response
- `backend/app/services/novedades/masters.py` — persistir `produccion`; posible update parcial
- `backend/app/api/routers/novedades.py` — responses
- `frontend/.../NovedadesParamPage.jsx` — botones + 2 modales
- Tests + runbook

## Approaches

1. **Reusar PUT único** — Modal editar (datos + produccion; sin tocar servicios o enviando ids actuales) + modal asociar (solo `servicio_ids` + campos actuales del módulo en el body).
   - Pros: API ya existe; menos endpoints
   - Cons: update “solo servicios” debe reenviar descripcion/valor
   - Effort: Low–Medium

2. **PATCH / split** — Endpoint parcial o `PUT .../servicios` aparte + PUT datos sin exigir servicios.
   - Pros: contratos más claros
   - Cons: más código vs lo ya armado
   - Effort: Medium

## Recommendation

Approach **1** salvo que survey pida API split (Q3). Migrar `produccion` boolean con default explícito (survey Q4).

## Risks

- Desasociar servicio usado en cargas históricas: ¿permitir? (Q6)
- Confusión nombre `produccion` vs check externo `tiene-produccion` en Carga (documentar semántica Q5).
- Trabajar en misma branch que `tiene-produccion-force` mezcla changes — preferir branch dedicada.

## Survey

Abierta en `decisions.md` (Q1–Q10). **No implementar** hasta cerrar.

## Ready for Proposal

Yes — survey Q1–Q10 closed (`decisions.md`).
