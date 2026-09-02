# Verify Report: novedades-capital-humano-export-liquidacion

## Scope
New Capital Humano download **Descargar liquidación** (`GET /novedades/export-liquidacion.xlsx`) producing `empresa|legajo|monto|concepto` for closed periods only, without changing existing exports.

## Results
- Backend: `159 passed` (`pytest`)
- Frontend: `vite build` OK

## Checklist
- [x] New button; existing XLS downloads unchanged
- [x] Closed period only (API 409 + UI disabled)
- [x] Cargas define rows by `concepto_liquidacion`; multi-servicio → multi-fila
- [x] Production/prácticas/internaciones allocated into carga rows (equal split / fallback)
- [x] Solo-producción with DEA/DEP/CAP/CAI → fixed conceptos 90/91/122/123
- [x] Missing servicio concepto → 422 with service names
- [x] Ajustes prorrateados
- [x] Unit tests in `backend/tests/test_liquidacion_export.py`
