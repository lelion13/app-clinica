# Design: Jefe profesionales + fecha realización

## Technical Approach

Extend Novedades domain: (1) RBAC + UI “Mis profesionales” for profesional↔servicio; (2) Alembic `fecha_realizacion` on assignment and novedad tables; validate against period range and “today”; surface in Carga form, grid, and XLS.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI superficie | New nav item under Novedades | Q2=B; keeps Param for full ABM |
| Who sees it | admin + rrhh + jefe | Q4=C |
| Disassociate | Always soft-delete link | Q3=A; cargas untouched |
| Date field | `DATE` `fecha_realizacion` on both carga tables | Q5=A |
| Validation | In period range AND ≤ today | Q6=D |
| Edit date | PUT while period open | Q9=B |
| Catalog pick | Active professionals, **typeahead** (reuse `ProfessionalCombobox` pattern), exclude already linked | Q1=B + R12 |
| Today | Calendar date at request time (align `BUSINESS_TIMEZONE` if already used elsewhere) | Q7 |

## Data Flow

```
Mis profesionales ──JWT──▶ profesional-servicios
                              ├─ assert_can_load_servicio (jefe) / all (admin|rrhh)
                              ├─ create link / soft-delete
                              └─ list filtered by scope

Carga create/update ──▶ PeriodGate open
                      ├─ fecha_realizacion in [inicio, fin]
                      ├─ fecha_realizacion <= today
                      └─ persist + list/export include both dates
```

## Schema changes

- `novedades_asignacion_modulo.fecha_realizacion` DATE NOT NULL (backfill: `created_at::date` or period start — prefer `created_at::date` capped into period)
- `novedades_novedad.fecha_realizacion` DATE NOT NULL (same backfill)
- Revision id short (≤32 chars), e.g. `0007_fecha_realizacion`

## File Changes

| File | Action |
|------|--------|
| `backend/alembic/versions/0007_*.py` | Create |
| `backend/app/models/novedades.py` | Modify |
| `backend/app/schemas/novedades.py` | Modify |
| `backend/app/services/novedades/cargas.py` | Validate date; list order unchanged |
| `backend/app/services/novedades/export_xls.py` | Column |
| `backend/app/api/routers/novedades.py` | Guards on profesional-servicios; response fields |
| `frontend/.../navigation.js` + `NovedadesNavMenu` | Item Mis profesionales |
| `frontend/src/components/ProfessionalCombobox.jsx` | Reuse | Typeahead nombre/DNI/matrícula (mismo patrón ocupación) |
| `frontend/.../NovedadesMisProfesionalesPage.jsx` | Create | Servicio + combobox + asociar/quitar |
| `frontend/.../NovedadesCargaPage.jsx` + grid | Date picker + column + edit; combobox en vez de select plano |
| `frontend/.../NovedadesXlsPage.jsx` | Column |
| `backend/tests/*` | RBAC + date validation |
| `docs/runbook.md` | Brief note |

## API sketch

```
GET/POST/DELETE /novedades/profesional-servicios  # guards: admin|rrhh|jefe (scoped)
GET /novedades/profesionales?servicio_id=&q=&exclude_linked=true  # optional query for picker

POST /novedades/asignaciones-modulos  { ..., fecha_realizacion: "YYYY-MM-DD" }
PUT  /novedades/asignaciones-modulos/{id}  { modulo_id?, fecha_realizacion? }  # period open
POST /novedades/cargas  { ..., fecha_realizacion }
PUT  /novedades/cargas/{id}  { tipo?, horas?, fecha_realizacion? }
```

## Testing Strategy

- Jefe 403 on foreign servicio for link create/delete
- Disassociate with existing cargas succeeds; professional absent from new carga list
- Create with date outside period → 422
- Create with tomorrow → 422
- Update fecha when closed → 409
- Export includes both date columns

## Open Questions

None blocking (survey closed).
