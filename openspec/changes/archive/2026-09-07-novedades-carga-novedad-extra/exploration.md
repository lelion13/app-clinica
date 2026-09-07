# Exploration: novedades-carga-novedad-extra

## Current State

- Módulo tiene flag `produccion` (Param).
- Carga (`NovedadesCargaPage`): si módulo seleccionado tiene `produccion=false`, **skip** de `GET .../bonos/tiene-produccion` y POST directo.
- Si check externo da `false` (módulo con prod o solo novedad) → modal force (Vacaciones/Enfermedad + obs) → POST con `motivo_sin_produccion` / `observacion_sin_produccion`.
- Botón submit UI: **Cargar novedad**. Spec estable: “Verificación de producción en Carga — flag módulo” + “Force-load sin producción”.

## User intent (survey)

Ver `decisions.md`.

## Affected Areas

- `frontend/src/pages/novedades/NovedadesCargaPage.jsx` — checkbox + skip/force branch
- `openspec/specs/novedades/spec.md` — delta sobre flag módulo / force-load
- Docs runbook (al apply)

## Approaches

1. **UI-only** — checkbox `novedadExtra`; si tildado → no check externo, abrir mismo force modal; limpiar/bloquear novedad horas; persistir solo motivo/obs existentes.
   - Pros: no migración; acopla a force-load ya documentado.
   - Cons: no hay flag explícito “novedad_extra” en DB (aceptado Q3).
   - Effort: Low

2. **Flag DB `novedad_extra`** — rechazado (Q3).

## Recommendation

Approach 1. Delta MODIFIED del requisito flag módulo + ADDED “Novedad extra en Carga”.

## Ready for Proposal

Yes.
