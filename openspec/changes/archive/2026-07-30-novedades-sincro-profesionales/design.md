# Design: Sync profesionales HTTP (Novedades)

## Technical Approach

Introduce table `novedades_profesional` as the only professionals source for Novedades. Sync from external HTTP API via `httpx` (already in deps). Rewire FKs from `professionals` → new table. Distribución MySQL sync untouched. Specs: catálogo aparte, sync manual, inactivo no carga, limpiar hard-delete.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Table | `novedades_profesional` (`codprof` UNIQUE string, `full_name`, `codprov`, `is_active` + AuditMixin) | Q1=A; avoid clash with `professionals` |
| PK column on cargas/links | Keep column name `professional_id` → FK `novedades_profesional.id` | Less churn in schemas/services |
| Match | Upsert by `codprof` as text; never `int()` | Leading zeros (Q2) |
| HTTP client | `httpx` + timeout settings | Already in `requirements.txt` |
| Secrets | `NOVEDADES_PROF_SYNC_URL`, `NOVEDADES_PROF_SYNC_TOKEN`, `NOVEDADES_PROF_SYNC_TIMEOUT` (default 30s) | Never log/return token |
| Failed fetch | Raise 502; **no** inactivate pass | Spec: don’t wipe on outage |
| Sync auth | `admin`/`rrhh` always; `jefe_medico` allowed on same endpoint | Q5=C (UI hides where needed) |
| Purge auth | `admin`/`rrhh` only | Q12=A |
| Purge | `DELETE` hard rows: asignacion_modulo, novedad, profesional_servicio | Q4=A / Q11=B |
| Migration FK swap | One-shot hard-delete same transactional tables, then drop/recreate FKs | Existing IDs point at `professionals`; cannot map by CODPROF. UI Limpiar remains for later ops (Q9) |
| Inactive in Mis prof. | List links with `is_active` flag; Carga/picker exclude inactive | Q7=C |
| `CODPROV` | Persist; omit from UI DTOs except optionally internal | Q8=B |
| Alembic id | `0008_novedades_profesional` (≤32) | Lesson F5 |

## Data Flow

```
[Param / Mis prof] ─JWT─▶ POST /novedades/profesionales/sync
                              │
                              ├─ GET {URL} Authorization: Bearer {TOKEN}
                              ├─ on HTTP/network fail → 502 (no DB inactivate)
                              └─ upsert by codprof; missing → is_active=false; back → true + update names

[Param] ─JWT─▶ POST /novedades/transaccional/purge  (confirm in UI)
                              └─ hard-delete 3 tables; return counts

Carga / directory ──▶ only novedades_profesional (active + linked)
```

## File Changes

| File | Action |
|------|--------|
| `backend/alembic/versions/0008_novedades_profesional.py` | Create table; purge transactional; retarget FKs |
| `backend/app/models/novedades.py` | Add `NovedadesProfesional`; FKs retarget |
| `backend/app/core/config.py` + `.env*.example` | Sync URL/token/timeout |
| `backend/app/services/novedades/prof_sync.py` | Create — fetch + upsert/inactivate |
| `backend/app/services/novedades/purge.py` | Create — hard-delete transactional |
| `backend/app/services/novedades/{helpers,professional_directory,cargas,export_xls}.py` | Use new model; enforce `is_active` on create |
| `backend/app/schemas/novedades.py` | Sync/purge response; directory `is_active`/`codprof` |
| `backend/app/api/routers/novedades.py` | `POST .../profesionales/sync`, `POST .../transaccional/purge` |
| `frontend/.../NovedadesParamPage.jsx` | Sync + Limpiar (confirm) + AlertModal summary |
| `frontend/.../NovedadesMisProfesionalesPage.jsx` | Sync button; show inactive links |
| `frontend/.../ProfessionalCombobox.jsx` / Carga | Active-only; match `codprof`+name |
| `docs/runbook.md` | Env, migrate, sync, purge order |
| `backend/tests/...` | Sync mock httpx; purge RBAC; inactive carga 422 |

## Interfaces / Contracts

```
POST /novedades/profesionales/sync
  → { created, updated, inactivated, skipped, errors[], synced_at }

POST /novedades/transaccional/purge
  → { deleted_asignaciones, deleted_novedades, deleted_profesional_servicios }

GET /novedades/profesionales?servicio_id&q&exclude_linked&include_inactive_links
  # default active-only for pickers; Mis prof. list uses links endpoint with is_active
```

External item shape: `{ "CODPROF": "001", "NOMBRES": "...", "CODPROV": "0001" }`.

## Testing Strategy

| Layer | What |
|-------|------|
| Unit | Upsert/reactivate/inactivate; no inactivate when fetch raises; `codprof` `"001"`≠`"1"` |
| API | Sync 403 operador; purge 403 jefe; carga inactive → 422; purge counts |
| Manual | Param sync+purge; Mis prof sync as jefe; Distribución `/profesionales` unchanged |

## Migration / Rollout

1. Backup DB (purge/migration destructive).
2. Deploy + `alembic upgrade head` (`0008_…`).
3. Set URL/token in `.env.prod`; rotate token if exposed.
4. Sync from Param → re-associate Mis profesionales → cargas.
5. Optional later: Limpiar from Param if need reset again.

## Open Questions

None blocking.
