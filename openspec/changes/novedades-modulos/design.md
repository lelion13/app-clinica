# Design: Novedades (módulos)

## Technical Approach

New Novedades domain in FastAPI/PostgreSQL + React pages under a second header dropdown. RBAC via extended `UserRole` and `deps` guards. Professionals via provider interface backed by `professionals` today.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Domain isolation | New tables under `novedades_*` | Mix into bookings | Clear swap later for HR source |
| Professionals v1 | `ProfessionalDirectory` adapter → `professionals` | Duplicate mock table | Owner Q10=C; swap later |
| XLS | Backend `openpyxl` stream download | Client-only CSV | Auth + consistent columns |
| Period uniqueness | Partial unique index / service check: one `open` | Soft flag only | Enforce Q7b in DB+service |
| Soft delete | Reuse `AuditMixin` | Hard delete | Matches clinic masters |
| Param UI | Single page tabs | Many menu items | Q13=A |

## Data Flow

```
UI Carga ──JWT──▶ API novedades ──▶ PeriodGate (must be open)
                      │
                      ├─▶ ModuleAssignment / Novedad services
                      ├─▶ Scope: jefe↔servicio N:N + profesional↔servicio N:N
                      └─▶ ProfessionalDirectory.list(service_id)

UI XLS ──JWT──▶ GET export ──▶ query filtros ──▶ openpyxl ──▶ file
```

## Entities (logical)

- `novedades_servicio` — id, nombre, activo
- `novedades_modulo` — id, descripcion, comentario, valor
- `novedades_jefe_servicio` — user_id × servicio_id (N:N)
- `novedades_profesional_servicio` — professional_id × servicio_id (N:N)
- `novedades_periodo` — nombre?, start, end, status open|closed
- `novedades_asignacion_modulo` — periodo, profesional, servicio, modulo, audit
- `novedades_novedad` — periodo, profesional, servicio, modulo (concepto), valor, justificacion (required), audit

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/user.py` | Modify | Add roles |
| `backend/alembic/versions/*` | Create | Enum + tables |
| `backend/app/api/deps.py` | Modify | Guards admin/rrhh/jefe |
| `backend/app/models/novedades/*.py` | Create | ORM |
| `backend/app/schemas/novedades/*.py` | Create | Pydantic |
| `backend/app/services/novedades/*.py` | Create | Business + period gate |
| `backend/app/api/routers/novedades/*.py` | Create | REST |
| `backend/app/services/novedades/professional_directory.py` | Create | Adapter |
| `frontend/src/config/navigation.js` | Modify | Group Novedades |
| `frontend/src/components/NovedadesNavMenu.jsx` | Create | Dropdown |
| `frontend/src/pages/novedades/*` | Create | Carga, Xls, Param |
| `frontend/src/pages/UsersPage.jsx` | Modify | Role options |
| `frontend/src/main.jsx` | Modify | Routes |
| `backend/tests/test_novedades_*.py` | Create | RBAC + period |

## Interfaces / Contracts (sketch)

```
GET/POST /api/v1/novedades/servicios
GET/POST /api/v1/novedades/modulos
GET/POST /api/v1/novedades/jefe-servicios
GET/POST /api/v1/novedades/periodos  (+ POST .../cerrar|reabrir)
GET/POST /api/v1/novedades/asignaciones-modulos
GET/POST /api/v1/novedades/cargas
GET /api/v1/novedades/export.xlsx?periodo&servicio&q&modulo
GET /api/v1/novedades/profesionales?servicio_id=
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit/API | RBAC matrix, period gate, justificacion | pytest |
| Integration | One open period; XLS content-type | pytest |
| Manual | Nav by role; tabs param; carga scoped | checklist |

## Migration / Rollout

Alembic: alter `userrole` enum; create novedades tables. Deploy migrate then app. No feature flag required if roles unused until seeded.

## Open Questions

- None blocking (survey closed). Optional later: seed demo servicios/módulos.
