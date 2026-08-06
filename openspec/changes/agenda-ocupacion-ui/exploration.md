# Exploration: agenda-ocupacion-ui

## Current State

- UI: `AgendaOcupacionPage.jsx` — grilla CSS día × consultorios (06–22), `PX_PER_HOUR=48`.
- Desalineación: columna HORA usa `height` + `borderBottom` (suma px); columnas de recursos pintan líneas con `position:absolute` a múltiplos exactos → drift vertical.
- Layout: contenedor con `overflowX:auto` y `minmax(120px,1fr)`; no usa altura de viewport; márgenes laterales del panel.
- Filtros UI actuales: solo `location_id` + día. Backend ya acepta `tipo`, `especialidad`, `medico`, `dia`, `id_dominio` + `filter-options`.
- “Sin consultorio”: resource `unassigned`; eventos sin `id_agenda` mapeado. Con filtros backend, debería reducirse; la UI aún no los envía.
- Detalle: `Popover` fixed anclado al click; solo botón Cerrar (sin Esc / outside / overlay).

## Affected Areas

- `frontend/src/pages/AgendaOcupacionPage.jsx` — layout, alineación, filtros, modal
- `backend/app/api/routers/distribucion.py` — ya expone query params (sin cambio API salvo verificación)
- `backend/app/services/distribucion/agenda_ocupacion.py` — filtros ya aplicados a todos los resources incl. unassigned
- `backend/tests/test_agenda_ocupacion.py` — casos filtro multi + unassigned si hace falta
- `docs/runbook.md` — nota UI breve

## Approaches

1. **Solo frontend + wire filtros existentes** — Fix box model / coordenadas compartidas; flex/grid viewport; multi-select desde `filter-options`; modal overlay.
   - Pros: sin migración; API lista; alcance acotado
   - Cons: multi-select nativo HTML limitado en móvil
   - Effort: Low–Medium

2. **Reintroducir FullCalendar resource timeline** — Reemplazar grilla custom.
   - Pros: alineación “gratis”
   - Cons: más peso; pierde look planilla acordado
   - Effort: High

## Recommendation

Approach **1**. Backend ya filtra; el gap es UI + bug de borde/box-sizing.

## Risks

- Multi-select nativo pesado con muchas opciones → MAY limitar altura / usar `size` o lista con checkboxes compacta.
- Altura viewport vs header/nav del panel → calcular `calc(100vh - …)` o flex en layout padre.

## Ready for Proposal

Yes.
