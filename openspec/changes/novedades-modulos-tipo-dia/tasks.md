# Tasks: novedades-modulos-tipo-dia

## Phase 1: Migration + model

- [x] 1.1 Alembic `0026_modulo_tipo_dia`: add `tipo_dia` NOT NULL default `semana`, backfill from `sadofe`, CHECK IN (`semana`,`sadofe`,`valor_unico`), drop `sadofe`
- [x] 1.2 `models/novedades.py`: replace `sadofe` with `tipo_dia` (str, default `semana`)

## Phase 2: Backend API + import

- [x] 2.1 `schemas/novedades.py`: `tipo_dia` on create/update/response; remove `sadofe`
- [x] 2.2 `masters.py` + `routers/novedades.py` `_modulo_response`: persist/expose `tipo_dia`
- [x] 2.3 `modulos_import.py`: header `tipo_dia`; dropdown values; empty→`semana`; invalid→row error; keep all-or-nothing

## Phase 3: Frontend

- [x] 3.1 `NovedadesParamPage.jsx`: three exclusive checks Semana·SADOFE·Valor único; create default Semana; edit keeps current; delete shows `Tipo día: …`
- [x] 3.2 `NovedadesCargaPage.jsx`: `moduloValidoParaFecha` by `tipo_dia` (valor_unico always); clear invalid selection on date change

## Phase 4: Tests + docs

- [x] 4.1 Update `test_novedades_sadofe_feriados.py` for default `tipo_dia=semana`
- [x] 4.2 Update `test_modulos_import.py`: plantilla headers + empty/invalid/`sadofe`/`valor_unico` cases
- [x] 4.3 `docs/runbook.md`: plantilla column `tipo_dia`; note `alembic upgrade head` for `0026`
