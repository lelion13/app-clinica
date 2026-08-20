# Design: capital-humano-grilla-actualizar

## Technical Approach

Reordenar UX de Capital Humano sin cambiar el pipeline de import/valorización. El botón **Actualizar** invoca el mismo import de bonos; la grilla pasa a totales fijos; el modal **Detalle** concentra el desglose.

## Architecture Decisions

### Decision: Actualizar = import bonos existente
**Choice**: Reutilizar `POST /novedades/capital-humano/bonos/import`.
**Rationale**: Q1; evita nuevo endpoint.

### Decision: Grilla sin columnas dinámicas
**Choice**: UI muestra solo totales; valorización sigue en backend para `monto_bonos` / Detalle.
**Rationale**: Q5/Q6; Excel llevará el desglose fino / concepto.

### Decision: Detalle unificado + ajuste en grilla
**Choice**: Extender Detalle (cargas + bonos valorizados + historial ajustes); mantener create ajuste desde fila.
**Rationale**: Q7.

### Decision: Default período open
**Choice**: Al cargar períodos, si hay uno `open`, setearlo como `periodoId`.
**Rationale**: Q3/Q8.

## Data Flow

```text
1. Mount → GET periodos + (si open) set periodoId → GET capital-humano
2. Actualizar (open) → POST bonos/import → toast/modal resumen → GET capital-humano
3. Detalle → GET grilla/detalle cargas + bonos del prof + ajustes del período
4. Agregar ajuste (grilla) → POST ajustes → refresh fila/grilla
```

## API

| Method | Path | Change |
|--------|------|--------|
| POST | `/capital-humano/bonos/import` | Sin cambio de contrato; caller = Actualizar |
| GET | `/capital-humano` | UI ignora columns dinámicas (MAY seguir viniendo) |
| GET | detalle / ajustes | Extender UI; endpoints existentes si alcanzan |

## File Changes

| File | Action |
|------|--------|
| `NovedadesXlsPage.jsx` | Modify |
| `capital_humano.py` / schemas | Modify si Detalle necesita payload unificado |
| `docs/runbook.md` | Modify |
| tests | Modify/add smoke de default período |

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| UI | default open, Actualizar closed disabled | manual / component |
| Backend | import unchanged | existing tests |
| Detalle | muestra bonos + ajustes | manual / API |

## Migration / Rollout

No migration.

## Open Questions

- [x] Survey closed — ver `decisions.md`.
