# Proposal: Sync profesionales HTTP para Novedades

## Intent

Separar el catálogo de profesionales de **Novedades** del de **Distribución de consultorios**, alimentando Novedades desde la API HTTP `GET /profesionales/activos` (Bearer), con sync manual, desactivación de ausentes y bloqueo de cargas sobre inactivos. Arranque limpio del data transaccional de Novedades vía botón de hard-delete controlado.

## Scope

### In Scope

- Nueva tabla/catálogo de profesionales **solo Novedades** (match por `CODPROF` string con leading zeros; campos `NOMBRES` + `CODPROV` persistido sin UI).
- Cliente HTTP + secrets por env (URL + token); endpoint sync JWT-protected.
- Botón **Sincronizar** en Parametrización (`admin`/`rrhh`) y Mis profesionales (`admin`/`rrhh`/`jefe_medico`).
- Sync: upsert por `CODPROF`; inactivar no vistos; reactivar si vuelven; resumen modal (creados/actualizados/inactivados/errores).
- Cargas (módulos/novedades) **solo** con profesional activo del catálogo Novedades; pickers/directory Novedades dejan de usar `professionals` de Distribución.
- Mis profesionales: vínculos a inactivos visibles para limpieza manual; sin ABM de alta/edición de profesionales.
- Botón **Limpiar cargas** solo en Parametrización (`admin`/`rrhh`): hard-delete de asignaciones módulo, novedades y vínculos profesional↔servicio; conserva servicios/módulos/períodos/jefes; modal de confirmación.
- Migración Alembic del esquema nuevo + rewire FKs Novedades al catálogo nuevo.
- Tests + runbook (env vars, sync, limpieza).
- Delta specs dominio `novedades` (y notas si aplica).

### Out of Scope

- Cambiar el sync MySQL / UI de Distribución (`/profesionales`).
- Mostrar o filtrar por `CODPROV` en UI.
- Sync automático programado (cron).
- Unificar catálogos Distribución ↔ Novedades.
- ABM manual de profesionales Novedades.

## Approach

1. Modelo `novedades_professionals` (nombre final en design) con `codprof` único, `full_name`, `codprov`, `is_active`, auditoría.
2. Servicio sync HTTP → upsert/inactivate/reactivate; respuesta tipo `ProfessionalSyncResponse`.
3. Rewire servicios Novedades (`cargas`, `professional_directory`, helpers, export) al nuevo modelo; enforce `is_active` en create.
4. UI: botones sync + modal resumen; Parametrización: limpiar + confirmación hard-delete.
5. Secrets: p.ej. `NOVEDADES_PROF_SYNC_URL`, `NOVEDADES_PROF_SYNC_TOKEN` (nombres exactos en design/runbook).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/models/` + Alembic | New/Modified | Catálogo Novedades; FKs cargas/vínculos |
| `backend/app/services/novedades/` | Modified | Directory, cargas, helpers, sync, purge |
| `backend/app/api/routers/novedades.py` | Modified | Endpoints sync + purge |
| `frontend/.../novedades/` | Modified | Parametrización, Mis profesionales |
| `docs/runbook.md` | Modified | Env + ops |
| `openspec/specs/novedades/` | Modified | Tras archive |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Hard-delete accidental | Med | Modal confirmación; solo admin/rrhh; Parametrización only |
| Token en chat/repo | High (ya expuesto) | Solo env; rotar; nunca loguear token |
| API externa caída / timeout | Med | 502 claro; no inactivar si el fetch falla |
| Leading zeros perdidos | Med | Tipo string end-to-end; no cast a int |
| Datos huérfanos si se limpia sin sync previo | Low | Orden ops documentado: limpiar → sync → reasociar |

## Rollback Plan

- Revert deploy + migration down si es segura; si ya hubo hard-delete, **no** hay restore automático (backup DB previo recomendado).
- Feature flag / deshabilitar endpoints sync-purge si hace falta.

## Dependencies

- API `https://api.cpmgsa.com.ar:8001/profesionales/activos` disponible con Bearer válido.
- Change archivado `novedades-jefe-profesionales-fecha-carga` (Mis profesionales, AlertModal).

## Success Criteria

- Distribución sigue usando `professionals` sin cambios funcionales de sync MySQL.
- Novedades lista/asocia/carga solo profesionales del catálogo sync HTTP.
- Sync inactiva ausentes, reactiva reaparecidos; inactivos no cargan módulos/novedades.
- Limpiar borra solo lo transaccional acordado, con confirmación.
- Roles de botones según Q5/Q12.
