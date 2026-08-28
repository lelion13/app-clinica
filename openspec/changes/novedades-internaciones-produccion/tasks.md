# Tasks: novedades-internaciones-produccion

## Phase 1: Configuration, Models & Migration

- [x] 1.1 Add `NOVEDADES_BONOS_PRACTICAS_URL`, `NOVEDADES_BONOS_INTERNACIONES_URL` and timeouts in `backend/app/core/config.py`.
- [x] 1.2 Define `NovedadesPracticaCantidad` and `NovedadesInternacionCantidad` models in `backend/app/models/novedades.py`.
- [x] 1.3 Create Alembic migration `backend/alembic/versions/0024_practicas_internaciones.py`.
- [x] 1.4 Update schemas in `backend/app/schemas/novedades.py` (import summary fields, detail items).

## Phase 2: Multi-Sync Service & Tariff Management

- [x] 2.1 Implement `_fetch_remote_practicas` and `_fetch_remote_internaciones` with normalization in `backend/app/services/novedades/bonos_import.py`.
- [x] 2.2 Implement atomic multi-snapshot sync (bonos + prácticas + internaciones) in `import_bonos_for_periodo`.
- [x] 2.3 Add special options ("Práctica traumatológica" and "Internaciones") in `backend/app/services/novedades/produccion_tarifas.py` for Parametrización.

## Phase 3: Valorization, Capital Humano Grid & Exports

- [x] 3.1 Update `build_capital_humano_rows` in `backend/app/services/novedades/capital_humano.py` to calculate prácticas and internaciones according to eligibility rules.
- [x] 3.2 Add endpoints/helpers to fetch professional prácticas and internaciones for the Detalle modal.
- [x] 3.3 Update `export-capital.xlsx` and `export-bonos.xlsx` in `backend/app/services/novedades/export_xls.py` to reflect the updated Total Producción and columns.

## Phase 4: Frontend UI (Capital Humano & Detalle Modal)

- [x] 4.1 Update `frontend/src/pages/novedades/NovedadesXlsPage.jsx` to display the enhanced sync summary on "Actualizar".
- [x] 4.2 Update Detalle modal in `NovedadesXlsPage.jsx` to render dedicated sections for Prácticas and Internaciones with subtotales.

## Phase 5: Testing, Documentation & Verification

- [x] 5.1 Add comprehensive unit tests in `backend/tests/test_bonos_import.py`.
- [x] 5.2 Update `docs/runbook.md`, `.env.example`, `.env.prod.example`.
- [x] 5.3 Run automated tests and verify clean execution.
