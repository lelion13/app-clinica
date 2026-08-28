# Archive report: 2026-08-28-novedades-modulos-import-excel

**Date:** 2026-08-28  
**Archived to:** `openspec/changes/archive/2026-08-28-novedades-modulos-import-excel/`

## Specs synced

| Domain | Action | Details |
|--------|--------|---------|
| `novedades` | Added | Plantilla Excel import módulos (dropdown servicios activos + Sí/No) |
| `novedades` | Added | Carga masiva módulos (todo o nada, reporte de errores por fila en modal) |
| `openspec/specs/README.md` | Updated | Origins catalog |

## Implementation artifacts

- Backend service: `backend/app/services/novedades/modulos_import.py`
- Backend endpoints: `backend/app/api/routers/novedades.py` (`/modulos/import/template`, `/modulos/import`)
- Backend schemas: `backend/app/schemas/novedades.py` (`ModuloImportRowError`, `ModuloImportResponse`)
- Frontend UI: `frontend/src/pages/novedades/NovedadesParamPage.jsx` (botones de descarga/carga + modal de feedback)
- Frontend API: `frontend/src/services/api.js` (`apiUploadWithRefresh`)
- Tests: `backend/tests/test_modulos_import.py`
- Packaging: `python-multipart` agregado a `backend/requirements.txt`

## Source of truth

`openspec/specs/novedades/spec.md`
