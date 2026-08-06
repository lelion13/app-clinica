# Tasks: Agenda ocupación — mejora UI visual

## Phase 1: Geometría y layout

- [x] 1.1 Unificar coordenadas verticales (absolute + border-box; sin drift HORA)
- [x] 1.2 Contenedor viewport / full-bleed, overflow interno, cabecera sticky
- [x] 1.3 Columnas `minmax(~160px)` + scroll horizontal

## Phase 2: Filtros

- [x] 2.1 Cargar `filter-options` al montar
- [x] 2.2 UI filtros (primera iteración: multi checkbox)
- [x] 2.3 Wire a `agenda/events` + recarga
- [x] 2.4 Sin consultorio respeta filtros (tests)
- [x] 2.5 **Ajuste UX:** selects de un valor en **una sola fila** (como Ubicación); maximizar grilla

## Phase 3: Modal detalle

- [x] 3.1 Modal centrado + overlay
- [x] 3.2 Cerrar Esc / overlay / Cerrar
- [x] 3.3 stopPropagation en panel

## Phase 4: Docs y verificación

- [x] 4.1 Tests backend filtros unassigned
- [x] 4.2 Runbook
- [x] 4.3 `implementation-notes.md` + update artefacts (decisions/design/spec/proposal)
- [x] 4.4 Change hermano `locations-tipo` (doc retroactiva fuera de SDD)
- [x] 4.5 Archive (2026-08-06); smoke VPS a cargo del operador post-deploy frontend

## Notes

- Contrato API sin cambios.
- Trabajo paralelo documentado: `locations-tipo`, split `nombre_agenda`, GHCR oauth (notes).
