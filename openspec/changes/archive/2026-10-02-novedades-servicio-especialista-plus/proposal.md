# Proposal: Plus especialista gated by service flag

## Intent

The +20% specialist factor on module loads must apply only when **both** the professional is `es_especialista` **and** the **service of the assignment** has a new Parametrización flag **Especialista**. Today the plus depends only on the professional, so loads in services that should not pay the plus are overvalued. Capital Humano Detalle must show which carga rows carry the plus (inferred).

## Scope

### In Scope
- DB/API/UI: servicio boolean `especialista` (label **Especialista**, like Activo); default **false** for existing and new
- Create asignación: `valor = catalog × 1.20` only if professional + service flags; else catalog
- Update asignación: do **not** re-apply specialist plus (fecha-only keeps valor; modulo change → catalog base without plus)
- Capital Humano Detalle Cargas: column **Plus esp.** Sí/— if `valor ≈ catalog × 1.20`
- Independent of `activo`

### Out of Scope
- Recalculating historical assignments (deferred)
- Excel export indicator
- Carga (jefe) UI badges
- Changing specialist sync / professional flag

## Approach

Migration + model/schemas/masters for `especialista`. Extend `modulo_valor_para_profesional` (or caller) with service flag. Wire create; stop plus on update. Expose catalog valor or computed `plus_especialista` on grilla rows for Detalle. Param UI checkbox.

## Affected Areas

| Area | Impact |
|------|--------|
| alembic `0028_…` | New |
| `models/novedades.py` Servicio | Modified |
| `schemas/novedades.py` | Modified |
| `masters.py`, `cargas.py`, `prof_sync.py` | Modified |
| `export_xls.py` GridRow (+ flag for Detalle) | Modified |
| `NovedadesParamPage.jsx` | Modified |
| `NovedadesXlsPage.jsx` Detalle | Modified |
| tests + runbook | Modified |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| After deploy all services OFF → new loads lose plus until toggled | Med | Document; RRHH enables intended services |
| Inference false positive/negative on Detalle | Low | Same quantize 0.01 as create |

## Rollback Plan

Revert FE/BE; migration downgrade drops column. Historical valores unchanged by this change.

## Dependencies

- Existing `es_especialista` on professional and assignment `valor` persistence

## Success Criteria

- [ ] Param shows Especialista checkbox; persisted
- [ ] Create applies plus only when both flags true
- [ ] Update does not re-apply plus
- [ ] Detalle shows Plus esp. for inferred rows
- [ ] Tests cover create/update/default
