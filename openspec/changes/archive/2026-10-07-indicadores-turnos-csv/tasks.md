# Tasks: indicadores-turnos-csv

## Phase 1: Backend

- [x] 1.1 Migration + models `turnos_csv_import` / `turnos_csv_row`
- [x] 1.2 Parse + normalize + match sync; reject unmatched
- [x] 1.3 Persist import (filename + period min/max Fecha Turno)
- [x] 1.4 Stats endpoint con filtros período + ubicación/room/esp/médico
- [x] 1.5 Router POST import + GET stats
- [x] 1.6 Tests

## Phase 2: Frontend

- [x] 2.1 Botón Importar + upload
- [x] 2.2 Modal unmatched
- [x] 2.3 Panel KPIs bajo torta; refresh con filtros

## Phase 3: Docs / ops

- [x] 3.1 Runbook
- [x] 3.2 Smoke + fix nginx `client_max_body_size 32m` (413 en CSV ~8MB)
- [x] 3.3 Verify + archive
