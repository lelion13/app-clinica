# Tasks: Agenda ocupación — mejora UI visual

## Phase 1: Geometría y layout

- [x] 1.1 Unificar coordenadas verticales en `AgendaOcupacionPage.jsx` (border-box / sin drift HORA vs líneas)
- [x] 1.2 Contenedor viewport: altura restante, overflow interno, cabecera sticky HORA+consultorios
- [x] 1.3 Subir `minmax` de columnas (~160px+) manteniendo scroll horizontal

## Phase 2: Filtros

- [x] 2.1 Cargar `GET .../ocupacion/agenda/filter-options` al montar
- [x] 2.2 UI multi-select tipo / especialidad / médico (select multiple o checkboxes compactos)
- [x] 2.3 Incluir selecciones en `agenda/events` query; recargar al cambiar
- [x] 2.4 Verificar que Sin consultorio respeta filtros (smoke + test)

## Phase 3: Modal detalle

- [x] 3.1 Reemplazar `Popover` por modal centrado + overlay
- [x] 3.2 Cerrar con Esc, clic overlay y botón Cerrar
- [x] 3.3 `stopPropagation` en el panel para no cerrar al interactuar dentro

## Phase 4: Verificación y docs

- [x] 4.1 Test backend: filtro tipo/especialidad/médico sobre eventos unassigned
- [x] 4.2 Actualizar `docs/runbook.md` (filtros + modal)
- [ ] 4.3 Smoke visual: alineación, viewport, filtros, cierre modal

## Notes

- Preferir cero cambio de contrato API.
- No tocar sync ni mapeo consultorios.
