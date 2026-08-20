# Proposal: Capital Humano — incluir solo-bonos de servicios especiales

## Intent

Incluir en la grilla principal de Capital Humano a profesionales con bonos importados del período para servicios `DEA`, `DEP`, `CAP`, `CAI`, aunque no tengan módulos/cargas.

## Scope

### In Scope
- Regla de inclusión en grilla principal para profesionales con bonos de opciones `servicio` exacto `DEA|DEP|CAP|CAI`.
- Esos profesionales dejan de aparecer en modal `Solo bonos`.
- Mantener `monto_total = monto_cargas + monto_ajustes` (sin valorización de bonos).
- Quitar selector de servicio en UI de Capital Humano (default operacional: todos los servicios).
- Incluir esos profesionales en `XLS agregado` y `XLS con bonos`.
- Documentación SDD y runbook.

### Out of Scope
- Cálculo monetario de bonos.
- Cambios de contrato en endpoints backend (`servicio_id` se mantiene por compatibilidad).
- Cambios fuera de Capital Humano.

## Approach

- Backend: extender construcción de filas de Capital Humano para unir `bonos_by_prof` y promover a grilla a quienes cumplan la regla de servicios especiales.
- Backend: ajustar listado `Solo bonos` para excluir los promovidos.
- Frontend: ocultar selector de servicio y dejar consultas sin `servicio_id`.
- Tests: casos de promoción a grilla y exclusión de modal Solo bonos.

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/app/services/novedades/capital_humano.py` | Modified |
| `backend/app/services/novedades/bonos_import.py` | Modified |
| `frontend/src/pages/novedades/NovedadesXlsPage.jsx` | Modified |
| `backend/tests/test_bonos_import.py` | Modified |
| `docs/runbook.md` | Modified |
| `openspec/specs/novedades/spec.md` | Modified (al archivar) |

## Risks

| Risk | Mitigation |
|------|------------|
| Inclusión incorrecta por comparación de texto | Match exacto a `DEA|DEP|CAP|CAI` |
| Doble presencia grilla + modal | Regla única de elegibilidad compartida |

## Rollback Plan

Revert de commit del change. Sin migraciones de datos.

## Success Criteria

- [ ] Un profesional con solo bonos `CAP` aparece en grilla principal.
- [ ] El mismo profesional no aparece en modal Solo bonos.
- [ ] `monto_total` no cambia por bonos (sigue cargas±ajustes).
- [ ] UI de Capital Humano no muestra selector de servicio.
- [ ] XLS agregado y XLS con bonos incluyen profesionales promovidos.
