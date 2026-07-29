# Tasks: novedades-sincro-profesionales

## Phase 1: Datos y config

- [x] 1.1 Add settings `NOVEDADES_PROF_SYNC_URL` / `_TOKEN` / `_TIMEOUT` in `backend/app/core/config.py` + `.env*.example` (no secrets)
- [x] 1.2 Create model `NovedadesProfesional` in `backend/app/models/novedades.py` (`codprof` unique str, `full_name`, `codprov`, `is_active`)
- [x] 1.3 Alembic `0008_novedades_profesional.py`: create table; hard-delete asignaciones/novedades/profesional_servicio; retarget FKs `professional_id` → `novedades_profesional.id`

## Phase 2: Backend sync + purge + rewire

- [x] 2.1 Create `backend/app/services/novedades/prof_sync.py` (httpx GET; upsert/reactivate/inactivate; fail → 502, no mass-inactivate)
- [x] 2.2 Create `backend/app/services/novedades/purge.py` (hard-delete 3 tables; return counts)
- [x] 2.3 Schemas sync/purge + directory fields (`codprof`, `is_active`) in `schemas/novedades.py`
- [x] 2.4 Rewire `helpers.py`, `professional_directory.py`, `cargas.py`, `export_xls.py` to `NovedadesProfesional`; reject inactive on create
- [x] 2.5 Router: `POST /novedades/profesionales/sync` (admin|rrhh|jefe); `POST /novedades/transaccional/purge` (admin|rrhh)

## Phase 3: Frontend

- [x] 3.1 Parametrización: botón Sync + resumen AlertModal; botón Limpiar + confirmación hard-delete
- [x] 3.2 Mis profesionales: botón Sync (admin/rrhh/jefe); listar vínculos inactivos visibles y desasociables
- [x] 3.3 Carga / pickers: solo activos catálogo Novedades; typeahead por nombre/`codprof`

## Phase 4: Tests y docs

- [x] 4.1 Tests: sync mock httpx (inactivate/reactivate/`001` zeros; no inactivate on fail)
- [x] 4.2 Tests: purge RBAC (jefe 403); carga inactive 422; sync jefe 200
- [x] 4.3 Update `docs/runbook.md` (env, migrate 0008, sync→reasociar, purge, rotate token)
- [x] 4.4 Mark tasks done; ready for verify/archive when accepted
