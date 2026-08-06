# Design: Agenda ocupación — mejora UI visual

## Technical Approach

Mejora UI-only (principalmente frontend) sobre la grilla CSS existente. Reutilizar endpoints `filter-options` y `agenda/events` sin cambiar contratos. Unificar geometría vertical; layout flex/calc; filtros multi en query; modal con backdrop + listeners Esc.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Mantener grilla CSS (no volver a FullCalendar) | Ya es planilla día×consultorio; el bug es box model, no el paradigma |
| `box-sizing: border-box` + altura fija sin border que sume, **o** eje HORA con líneas absolutas igual que resources | Elimina drift acumulado de `borderBottom` en labels |
| Contenedor grilla: `flex: 1; minHeight: 0; overflow: auto` bajo columna de página `height: calc(100vh - offset)` | Q1=C: scroll interno; sticky header con `position: sticky; top: 0` en fila de títulos |
| `minmax(160px, 1fr)` (o similar) para columnas | Columnas más generosas; scroll-x si hay muchas |
| `<select multiple>` o lista de checkboxes compacta alimentada por `filter-options` | Q3=A multi-select; checkboxes si `<select multiple>` es pobre en UX móvil |
| Query: repetir `tipo=`, `especialidad=`, `medico=` (FastAPI `list[str]`) | Ya soportado en router |
| Modal: `position:fixed` overlay + panel centrado; `useEffect` keydown Escape; overlay `onClick` cierra; stopPropagation en panel | Q4=B |
| Backend: no cambiar filtro unassigned salvo bug | Spec ya exige mismos filtros; verificar con test |

## Data Flow

```
mount / day|filters change
  → GET filter-options (una vez o al mount)
  → GET agenda/events?start&end&location_id&tipo*&especialidad*&medico*
  → resources + events (incl. unassigned filtrado)
  → render grid
click bloque → setModal(detail)
Esc | overlay click | Cerrar → clear modal
```

## File-Level Changes

| File | Change |
|------|--------|
| `frontend/src/pages/AgendaOcupacionPage.jsx` | Layout viewport; fix hora; state filtros; load filter-options; modal |
| `backend/tests/test_agenda_ocupacion.py` | Test multi-filtro reduce unassigned |
| `docs/runbook.md` | Nota UI filtros + modal |
| `backend/.../agenda_ocupacion.py` | Solo si verificación falla |

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| FullCalendar resource view | Pierde look planilla; más refactor |
| Filtrar unassigned solo en cliente | Duplica lógica; backend ya filtra |

## Testing Strategy

- Backend: filtro `tipo` con 2 filas unassigned → solo 1 evento.
- Manual: alineación 08:00; viewport scroll; Esc/overlay; multi-select.

## Migration / Rollout

Sin migración. Deploy frontend (+ backend si tests). Smoke en `/agenda-ocupacion`.
