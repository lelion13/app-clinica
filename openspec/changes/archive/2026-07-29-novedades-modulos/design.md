# Design: Novedades (módulos)

## Technical Approach

New Novedades domain in FastAPI/PostgreSQL + React pages under a second header dropdown. RBAC via extended `UserRole` and `deps` guards. Professionals via provider interface backed by `professionals` today.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Domain isolation | New tables under `novedades_*` | Mix into bookings | Clear swap later for HR source |
| Professionals v1 | `ProfessionalDirectory` adapter → `professionals` | Duplicate mock table | Owner Q10=C; swap later |
| XLS | Backend `openpyxl` stream download | Client-only CSV | Auth + consistent columns |
| Period uniqueness | Service check: one `open` | Soft flag only | Enforce Q7b in DB+service |
| Soft delete | Reuse `AuditMixin` | Hard delete | Matches clinic masters |
| Param UI | Single page tabs | Many menu items | Q13=A |
| Valor hora | Column on `novedades_servicio` | Global `novedades_config` only | R3 — valor por servicio |
| Novedad payload | `tipo` + `horas` | Concepto=módulo + justificación | R2 / Q14 reemplazado |
| Módulo↔servicio | N:N join table | Módulo global sin filtro | R4 |
| List scope jefe | `scoped_servicio_ids` en listados | Filtro solo en UI | R7 — no filtrar en cliente |
| Carga list UI | `CargasListGrid` unificada | Dos `<ul>` | R9 |
| Anular UX | Modal confirmación | `window.confirm` | R10 |

## Data Flow

```
UI Carga ──JWT──▶ API novedades ──▶ PeriodGate (must be open)
                      │
                      ├─▶ ModuleAssignment / Novedad services
                      ├─▶ Scope: jefe↔servicio N:N + profesional↔servicio N:N
                      ├─▶ Listados: filter por scoped_servicio_ids + order servicio/profesional
                      └─▶ ProfessionalDirectory.list(service_id)

UI XLS ──JWT──▶ GET grilla|export ──▶ query filtros ──▶ openpyxl ──▶ file
```

## Entities (logical)

- `novedades_servicio` — id, nombre, activo, **valor_hora**
- `novedades_modulo` — id, descripcion, comentario, valor
- `novedades_modulo_servicio` — modulo_id × servicio_id (N:N)
- `novedades_jefe_servicio` — user_id × servicio_id (N:N)
- `novedades_profesional_servicio` — professional_id × servicio_id (N:N)
- `novedades_periodo` — nombre?, start, end, status open|closed
- `novedades_asignacion_modulo` — periodo, profesional, servicio, modulo, audit
- `novedades_novedad` — periodo, profesional, servicio, **tipo**, **horas**, audit (sin justificación; valor calculado en lectura/export)
- `novedades_config` — legado/seed; valor_hora global migrado a servicios en `0006`

## Migrations

| Rev | Contenido |
|-----|-----------|
| `0004_novedades_modulos` | Roles + tablas base Novedades |
| `0005_novedades_horas_valor` | Novedad tipo/horas; valor hora config |
| `0006_mod_svc_valor_hora` | N:N módulo↔servicio; `valor_hora` en servicio (id corto ≤32 chars) |

**Fix:** el revision id original `0006_novedades_modulo_servicio_valor_hora` excedía `alembic_version.version_num` VARCHAR(32); se acortó a `0006_mod_svc_valor_hora`.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/user.py` | Modify | Roles `jefe_medico`, `rrhh` |
| `backend/alembic/versions/0004–0006*` | Create | Enum + tablas + evoluciones |
| `backend/app/api/deps.py` | Modify | Guards admin/rrhh/jefe/reader |
| `backend/app/models/novedades.py` | Create | ORM |
| `backend/app/schemas/novedades.py` | Create | Pydantic (respuestas enriquecidas con nombres) |
| `backend/app/services/novedades/*` | Create | Masters, cargas, export, helpers (`scoped_servicio_ids`) |
| `backend/app/api/routers/novedades.py` | Create | REST `/api/v1/novedades/*` |
| `frontend/src/config/navigation.js` | Modify | Grupo Novedades |
| `frontend/src/components/NovedadesNavMenu.jsx` | Create | Dropdown |
| `frontend/src/pages/novedades/NovedadesCargaPage.jsx` | Create | Formulario carga |
| `frontend/src/pages/novedades/CargasListGrid.jsx` | Create | Grilla filtrable/ordenable + modal anular |
| `frontend/src/pages/novedades/NovedadesParamPage.jsx` | Create | Tabs param |
| `frontend/src/pages/novedades/NovedadesXlsPage.jsx` | Create | Grilla + download |
| `frontend/src/pages/UsersPage.jsx` | Modify | Role options |
| `frontend/src/main.jsx` | Modify | Routes + `ProtectedRoute` roles |
| `backend/tests/test_novedades_*.py` / `test_rbac_deps.py` | Create | RBAC + period + scope helpers |
| `docs/runbook.md` | Modify | Roles, migrate, flujo Novedades |

## Interfaces / Contracts

```
GET/POST /api/v1/novedades/servicios
GET/POST /api/v1/novedades/modulos?servicio_id=
GET/POST /api/v1/novedades/jefe-servicios
GET/POST /api/v1/novedades/profesional-servicios
GET/POST /api/v1/novedades/periodos  (+ .../cerrar|reabrir)
GET/POST /api/v1/novedades/asignaciones-modulos   # GET scoped + order servicio/profesional
GET/POST/DELETE /api/v1/novedades/cargas          # GET scoped + order
GET /api/v1/novedades/grilla
GET /api/v1/novedades/export.xlsx?...
GET /api/v1/novedades/profesionales?servicio_id=
```

**List response enrichment:** asignaciones y novedades incluyen `servicio_nombre`, `professional_name`, `periodo_nombre` (además de IDs).

**Novedad create body:** `{ periodo_id, servicio_id, professional_id, tipo, horas }`  
**Asignación create body:** `{ periodo_id, servicio_id, professional_id, modulo_id }`

## Frontend notes (Carga)

- Evitar flash “No hay profesionales…” con flag `loadingServicio` mientras llegan pros/módulos del servicio.
- Anular: modal con resumen; errores de DELETE se muestran en el modal (el callback `onAnular` debe propagar throw).

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit/API | RBAC matrix, period gate, scope jefe | pytest |
| Unit | `scoped_servicio_ids` admin vs jefe | pytest |
| Integration | One open period; XLS content-type | pytest |
| Manual | Nav by role; tabs param; carga scoped; modal anular; grilla sort/filter | checklist |

## Migration / Rollout

Alembic `upgrade head` after deploy (`0004`→`0006`). No feature flag; seed roles/asociaciones antes de uso real.

## Open Questions

- None blocking. Optional later: seed demo; editar asociaciones módulo↔servicio en UI update; liquidación/PDF/emails.
