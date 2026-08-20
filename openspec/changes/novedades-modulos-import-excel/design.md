# Design: novedades-modulos-import-excel

## Technical Approach

En tab Módulos: descargar plantilla XLSX (openpyxl + DataValidation de servicios y Sí/No) y POST multipart de import con validación completa previa; commit atómico (todo o nada). Errores → modal fila+motivo.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| 1 servicio/fila | Columna `servicio` + dropdown nombres activos | Q1 |
| Duplicados | Error si `descripcion` ya existe (no deleted) | Q2 |
| Commit | Validate all first; then insert all in one transaction | Q3 |
| Bools | Sí/No (case-insensitive) | Q4 |
| Valor | Vacío/null → 0 | Q5 |
| UX resultado | Modal lista errores; si OK, toast/aviso + refresh lista | Q6 |
| Match servicio | Nombre trim, case-insensitive, solo `activo` | Anti-ambigüedad |
| Filas vacías | Ignorar filas sin descripción ni servicio | Práctico |

## Data Flow

```text
Plantilla: GET /novedades/modulos/import/template
  → servicios activos → hoja _servicios + DataValidation en col servicio
  → DataValidation Sí/No en produccion, sadofe

Import: POST /novedades/modulos/import (multipart file)
  1. Parse filas
  2. Collect errors (dup, servicio desconocido, valor inválido, Sí/No inválido, desc vacía…)
  3. If any error → 400 + { errors: [{row, reason}] }  (no DB writes)
  4. Else create_modulo each → 200 + { created: N }
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `services/novedades/modulos_import.py` | Create | template + import validate/commit |
| `schemas/novedades.py` | Modify | ImportErrorItem, ImportResult |
| `api/routers/novedades.py` | Modify | GET template + POST import (admin/rrhh) |
| `NovedadesParamPage.jsx` | Modify | botones + file input + modal errores |
| `docs/runbook.md` | Modify | columnas plantilla |

## Interfaces / Contracts

**Plantilla columnas (fila 1 headers):**  
`descripcion` | `comentario` | `valor` | `produccion` | `sadofe` | `servicio`

**Errores ejemplo:**  
`Fila 5: ya existe un módulo con esa descripción`  
`Fila 7: servicio no encontrado o inactivo: UTI`

## Testing Strategy

| Layer | What |
|-------|------|
| Unit | parse Sí/No; valor vacío→0; match servicio |
| Unit | error → 0 inserts; ok → N inserts |
| Unit | duplicado descripción |
| UI smoke | plantilla download; modal errores |

## Migration / Rollout

No migration. Deploy backend+frontend.

## Open Questions

None.
