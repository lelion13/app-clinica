# Design: capital-humano-profesionales-especialistas

## Technical Approach

Persistir `es_especialista` en catálogo; enriquecer sync de Param con segundo GET; aplicar factor 1.20 solo al **crear** asignación de módulo; exponer flag en Detalle CH.

## Architecture Decisions

### Decision: Sync solo Param
**Choice**: Mis profesionales no llama especialistas.
**Rationale**: Q3.

### Decision: Plus al persistir módulo
**Choice**: Columna `valor` en `novedades_asignacion_modulo`; al create/update módulo `valor = catalogo × 1.20` si especialista. Lecturas CH/export usan ese valor.
**Rationale**: Q1/Q2; el modelo previo leía siempre `modulo.valor` del catálogo — hacía falta snapshot en la asignación.
### Decision: Fallo parcial
**Choice**: No revertir catálogo; no mutar flags; warning en response.
**Rationale**: Q4.

## Data Model

```text
novedades_profesional.es_especialista  BOOLEAN NOT NULL DEFAULT false
```

## Data Flow

```text
Param → POST /profesionales/sync
  1. sync catálogo (existente)
  2. GET NOVEDADES_PROF_ESPECIALISTAS_URL
  3a. OK → set flags; unmatched[]
  3b. fail → warning; flags untouched
  4. UI modal unmatched / warning

Carga módulo → create asignación
  if prof.es_especialista: valor *= 1.20

CH Detalle → mostrar es_especialista del row/prof
```

## API

| Change | Notes |
|--------|-------|
| `NovedadesProfSyncResponse` | + `especialistas_unmatched`, `especialistas_warning` (optional) |
| Capital Humano row and/or Detalle | Expose `es_especialista` (prefer on grid row for Detalle header) |
| Env | `NOVEDADES_PROF_ESPECIALISTAS_URL`, optional timeout |

## Testing Strategy

| Layer | What |
|-------|------|
| Unit | match CODPROF; set/clear flags; unmatched list |
| Unit | create módulo ×1.20 vs novedad sin plus |
| Unit | fail especialistas → flags unchanged |
| UI smoke | modal Param; badge Detalle CH |

## Migration / Rollout

1. `alembic upgrade head`
2. Set `NOVEDADES_PROF_ESPECIALISTAS_URL` in `.env.prod`
3. Sync desde Param
