# Design: Capital Humano + LEGAJO

## Approach

Add `legajo` to sync catalog; new table `novedades_ajuste_capital`; Capital Humano UI aggregates by professional; dual XLS.

## Decisions (from survey)

See `decisions.md` Q1–Q11.

## Schema

- `novedades_profesional.legajo` VARCHAR(40) NULL
- `novedades_ajuste_capital`: id, professional_id, periodo_id, servicio_id NULL, importe Numeric(12,2) ≠ 0, comentario, audit
- Alembic `0009_capital_humano_legajo`

## API

```
GET  /novedades/capital-humano          # aggregated rows
POST /novedades/capital-humano/ajustes  # create signed importe
GET  /novedades/capital-humano/ajustes?professional_id&periodo_id&servicio_id?
GET  /novedades/export-capital.xlsx     # aggregated
GET  /novedades/export.xlsx             # detail (existing)
```

## Files

| File | Action |
|------|--------|
| `0009_capital_humano_legajo.py` | Create |
| models/schemas/prof_sync | Modify |
| `services/novedades/capital_humano.py` | Create |
| router + export_xls | Modify |
| `NovedadesXlsPage.jsx` + nav | Modify |
| tests + runbook | Modify |
