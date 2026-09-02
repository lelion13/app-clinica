# Design: novedades-capital-humano-export-liquidacion

## Technical Approach

Add a dedicated export builder that does not alter `build_capital_humano_rows` response shape. Reuse loaders for snapshots, tarifas, and eligibility already used by Capital Humano.

## Algorithm (`build_liquidacion_rows`)

```
1. Load periodo; if not closed → 409/422
2. Load detail cargas for periodo (asignaciones + novedades) with servicio.concepto_liquidacion
3. If any carga service has null concepto → 422 with service names
4. Group carga montos by (professional_id, concepto)
5. Load eligible valorized production per professional (bonos/practicas/internaciones)
6. Bucket production by empresa from centro/sucursal prefix (SC→CHI else CMG)
7. For each professional:
   a. If has carga conceptos:
      - For each production empresa bucket:
        targets = conceptos of that empresa among cargas
        if empty: targets = all carga conceptos
        add bucket/len(targets) to each target
   b. Else if has special bonos DEA|DEP|CAP|CAI:
      - Build fixed conceptos present from special bonos (90/91/122/123)
      - Split production buckets equally onto fixed conceptos of matching empresa;
        if no match, onto all fixed conceptos
   c. Else: skip professional (unless only ajustes — then skip ajustes too)
8. Split ajustes equally onto that professional’s conceptos (carga or fixed)
9. Aggregate to (empresa, legajo, concepto) → monto
10. Sort stably (empresa, legajo, concepto)
11. Write XLS via openpyxl
```

## Fixed concept map

| empresa | servicio special | concepto |
|---------|------------------|----------|
| CMG | DEA, CAI | 90 |
| CMG | DEP, CAP | 91 |
| CHI | DEA, CAI | 123 |
| CHI | DEP, CAP | 122 |

## API

- `GET /novedades/export-liquidacion.xlsx?periodo_id={id}`
- Auth: `require_admin_or_rrhh`
- Response: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

## Files

| File | Change |
|------|--------|
| `backend/app/services/novedades/liquidacion_export.py` | **Create** builder + xlsx |
| `backend/app/api/routers/novedades.py` | Add endpoint |
| `frontend/src/pages/novedades/NovedadesXlsPage.jsx` | Button Descargar liquidación |
| `backend/tests/test_liquidacion_export.py` | Unit tests |
| `docs/runbook.md` | Document button + rules |

## Non-goals / safety

- Do not change `export_capital_xlsx_bytes` / bonos export.
- Do not change grid aggregation or Actualizar sync.
