# Design: capital-humano-bonos-servicios-especiales

## Technical Approach

Se reutiliza la importación/persistencia de bonos existente. El cambio se concentra en la elegibilidad de filas para la grilla principal de Capital Humano.

## Architecture Decisions

### Decision: Regla de promoción a grilla
**Choice**: Promover profesionales con bonos si existe al menos una opción con `servicio` exacto en `DEA`, `DEP`, `CAP`, `CAI`.
**Alternatives considered**: incluir cualquier servicio, o match por catálogo profesional↔servicio.
**Rationale**: requisito explícito del negocio.

### Decision: Filtro servicio solo UI
**Choice**: quitar selector en frontend y no enviar `servicio_id`.
**Alternatives considered**: eliminar soporte backend.
**Rationale**: menor riesgo y compatibilidad.

## Data Flow

1. `load_bonos_snapshot(periodo)` retorna columnas y `bonos_by_prof`.
2. `build_capital_humano_rows(...)` parte de cargas/ajustes.
3. Si `include_bonos=True`, analiza bonos por profesional:
   - si ya está en grilla: se mantiene.
   - si no está, pero tiene opción con `servicio` especial: se agrega con montos 0.
4. `list_solo_bonos(...)` excluye profesionales promovidos.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/novedades/capital_humano.py` | Modify | Regla de promoción de solo-bonos especiales a grilla |
| `backend/app/services/novedades/bonos_import.py` | Modify | Reuso de regla para filtrar modal Solo bonos |
| `frontend/src/pages/novedades/NovedadesXlsPage.jsx` | Modify | Ocultar select de servicio y no enviar `servicio_id` |
| `backend/tests/test_bonos_import.py` | Modify | Tests de promoción DEA/DEP/CAP/CAI |
| `docs/runbook.md` | Modify | Nota de comportamiento actualizado |

## Interfaces / Contracts

- No cambia el contrato público de endpoints.
- `servicio_id` sigue soportado en backend.
- UI Capital Humano deja de exponer filtro de servicio.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit backend | elegibilidad por servicio especial | tests en service |
| Integration backend | solo-bonos excluye promovidos | tests de listados |
| UI smoke | selector servicio oculto, grilla y modal coherentes | prueba manual |

## Migration / Rollout

No migration required.

## Open Questions

- [ ] La valorización monetaria de bonos se tratará en un change separado.
