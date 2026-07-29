# Exploration: Jefe gestiona profesionales + fecha de realización en carga

## Current State

- ABM **profesional↔servicio** existe en Parametrización (`/novedades/profesional-servicios`) pero solo `admin`/`rrhh` (`require_admin_or_rrhh`).
- `jefe_medico` ya carga módulos/novedades solo en **sus** servicios; el listado de profesionales en Carga viene del ABM filtrado por servicio.
- Cargas (`novedades_asignacion_modulo`, `novedades_novedad`) tienen `created_at` (auditoría) pero **no** una fecha de realización del hecho clínico/operativo.
- Grilla Carga / XLS muestran “fecha carga” = timestamp de alta, no día del módulo/novedad.
- Spec estable: `openspec/specs/novedades/spec.md` (post-archive `novedades-modulos`).

## Affected Areas

- `backend/app/api/routers/novedades.py` — ampliar RBAC profesional-servicios; campos fecha en create/list/export
- `backend/app/services/novedades/cargas.py` + schemas/models + Alembic
- `backend/app/services/novedades/export_xls.py` — columna nueva
- `frontend/src/pages/novedades/NovedadesParamPage.jsx` y/o nueva UI para jefe
- `frontend/src/pages/novedades/NovedadesCargaPage.jsx` + `CargasListGrid.jsx` + XLS page
- `openspec/specs/novedades/spec.md` — delta al cerrar

## Approaches

### A. Jefe: mismo ABM scoped vs pantalla dedicada

1. **Reutilizar tab Parametrización (scoped)** — jefe entra a Param (solo tab profesionales↔servicios, solo sus servicios).
   - Pros: poco UI nuevo; misma API
   - Cons: hoy Param es “admin/rrhh”; hay que partir menú/tabs por rol
   - Effort: Medium

2. **Sección en Carga o ítem nav “Mis profesionales”** — UI solo jefe/admin para asociar.
   - Pros: no contamina Param completa
   - Cons: otra superficie
   - Effort: Medium

### B. Fecha de realización

1. **Campo `fecha_realizacion` (date) required** en asignación y novedad; date picker en form; columna en grilla/XLS.
   - Pros: simple, claro para RRHH
   - Cons: hay que definir validación vs rango del período
   - Effort: Low–Medium

2. **Datetime** — overnight / turnos.
   - Pros: más preciso
   - Cons: overkill si RRHH trabaja por día
   - Effort: Medium

## Recommendation

- Jefe: **scoped write** sobre profesional↔servicio (API + UI); admin/rrhh conservan ABM global. Preferencia de superficie UI a cerrar en survey.
- Fecha: **date** (día) requerida en ambas cargas; export/grilla; validación vs período a cerrar en survey.
- No incluir sync con sistema externo de profesionales en este change.

## Risks

- Quitar profesional con cargas históricas/abiertas: soft-delete del link vs bloqueo
- Fecha fuera del período abierto: confusión contable vs realidad clínica
- Jefe con acceso parcial a Param puede ver/tocar otras pestañas si el guard UI falla

## Ready for Proposal

Yes — proposal draft + survey abierta (una pregunta a la vez).
