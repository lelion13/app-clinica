# Design: novedades-modulos-tipo-dia

## Technical Approach

Replace boolean `novedades_modulo.sadofe` with string `tipo_dia` (`semana` | `sadofe` | `valor_unico`). One Alembic revision backfills then drops `sadofe`. API/schemas/import/UI switch atomically (same FE+BE deploy). Carga filter stays UI-only; `valor_unico` always eligible.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Storage | `VARCHAR` + CHECK | Postgres ENUM | Matches existing bool→string pattern; easy Alembic |
| API | Only `tipo_dia` | Dual `sadofe`+`tipo_dia` | Survey Q5; avoid dual-write |
| Carga filter | FE `moduloValidoParaFecha` | Backend reject | Survey Q4; same as today |
| Excel | Column `tipo_dia` exact tokens | Sí/No map | Survey Q3/Q9; empty→`semana` |
| Param UI | Three exclusive checks | Radio / select | Survey Q6; order Semana·SADOFE·Valor único |

## Data Flow

```
Excel/Plantilla ──tipo_dia──→ modulos_import ──→ NovedadesModulo
Param create/edit ──tipo_dia──→ masters + schemas ──→ API JSON
Carga fecha + feriados ──→ moduloValidoParaFecha(tipo_dia) ──→ combo
```

Filter rules:
- `semana` ↔ Mon–Fri and not holiday
- `sadofe` ↔ Sat/Sun or holiday
- `valor_unico` ↔ always

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/alembic/versions/0026_modulo_tipo_dia.py` | Create | Add `tipo_dia`, backfill, drop `sadofe`, CHECK |
| `backend/app/models/novedades.py` | Modify | `tipo_dia` replaces `sadofe` |
| `backend/app/schemas/novedades.py` | Modify | create/update/response: `tipo_dia` |
| `backend/app/services/novedades/masters.py` | Modify | persist `tipo_dia` |
| `backend/app/services/novedades/modulos_import.py` | Modify | header + parse + template dropdown |
| `backend/app/api/routers/novedades.py` | Modify | `_modulo_response` |
| `frontend/.../NovedadesParamPage.jsx` | Modify | 3 exclusive checks + delete label |
| `frontend/.../NovedadesCargaPage.jsx` | Modify | filter by `tipo_dia` |
| `backend/tests/test_novedades_sadofe_feriados.py` | Modify | default `tipo_dia=semana` |
| `backend/tests/test_modulos_import.py` | Modify | `tipo_dia` column/cases |
| `docs/runbook.md` | Modify | plantilla + migrate note |

## Interfaces / Contracts

```python
TIPO_DIA_VALUES = ("semana", "sadofe", "valor_unico")
# ModuloCreateRequest / Update / Response: tipo_dia: Literal[...] = "semana"
# No sadofe field
```

Excel headers: `descripcion`, `comentario`, `valor`, `produccion`, `tipo_dia`, `servicio`.

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | Schema default `semana`; invalid rejected | Pydantic / existing tests |
| Import | empty→semana; invalid→row error; no partial commit | `test_modulos_import.py` |
| FE logic | filter semana/sadofe/valor_unico | keep/extend if helpers tested; manual QA |

## Migration / Rollout

1. Deploy BE+FE together after `alembic upgrade head` (`0026`).
2. Backfill: `sadofe=false`→`semana`, `true`→`sadofe`; no row gets `valor_unico`.
3. Re-download plantilla; old `sadofe` column ignored / missing `tipo_dia`→`semana`.

## Open Questions

None — survey Q1–Q10 closed.
