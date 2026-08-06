# Design: Agenda ocupación — mejora UI visual

## Technical Approach

UI-first sobre grilla CSS. Reutilizar `filter-options` y `agenda/events`. Geometría vertical compartida; layout full-bleed + flex; filtros = selects de un valor en una fila; modal overlay + Esc.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Mantener grilla CSS | Planilla día×consultorio; bug era box model |
| Marcas de hora `absolute` + `border-box` (igual que resources) | Evita drift por `borderBottom` en flujo normal |
| Full-bleed `100vw` + `marginLeft: calc(50% - 50vw)` | Sale del `maxWidth:1180` del `AppLayout` |
| `height: calc(100dvh - ~112px)` + grilla `flex:1; overflow:auto` | Q1=C; maximiza área útil |
| Sticky header de columnas `top:0` + HORA `left:0` | Orientación al scrollear |
| `minmax(160px, 1fr)` | Columnas legibles |
| **Selects single-value** (no multi checkbox) | Post-deploy: multi robaba altura; grilla es la prioridad |
| Query con 0–1 valor por eje (API aún acepta `list[str]`) | Compatible con backend existente |
| Modal fixed overlay + Esc + stopPropagation | Q4=B |

## Data Flow

```
mount → GET filter-options + GET /locations
day|filters change → GET agenda/events?start&end&location_id&tipo&especialidad&medico
→ resources + events (unassigned filtrado)
click bloque → modal(detail)
Esc | overlay | Cerrar → close
```

## File-Level Changes

| File | Change |
|------|--------|
| `AgendaOcupacionPage.jsx` | Layout, FilterSelect, modal, alineación |
| `test_agenda_ocupacion.py` | Filtros tipo/médico unassigned |
| `docs/runbook.md` | UI + filtros una fila |
| `implementation-notes.md` | Aprendizajes + fuera de SDD |

## Alternatives Considered

| Alternative | Why Rejected / Changed |
|-------------|------------------------|
| FullCalendar resources | Pierde look planilla |
| Multi-select checkboxes (Q3=A) | Implementado y **revertido**: ocupaba 2+ filas; grilla no dominante |
| Filtrar unassigned solo en cliente | Backend ya filtra |

## Testing Strategy

- Backend: filtro tipo/médico reduce unassigned.
- Manual: alineación 08:00; una fila de filtros; Esc/overlay; Sin consultorio.

## Migration / Rollout

Sin migración en este change. Deploy **frontend** (y backend si aún falta ola ocupación). Ver `implementation-notes.md` §E (GHCR).
