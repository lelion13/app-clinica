# Proposal: Agenda ocupación — mejora UI visual

## Intent

Mejorar legibilidad y usabilidad de `/agenda-ocupacion`: alineación hora↔filas, mejor uso del viewport, filtros que reduzcan “Sin consultorio”, y modal de detalle cerrable con Esc/overlay.

## Scope

### In Scope

- Fix alineación vertical HORA ↔ celdas/líneas de hora.
- Layout Q1=C: ancho completo, altura al viewport, scroll interno, header sticky, columnas más anchas.
- Filtros multi-select UI: tipo, especialidad, médico (opciones vía `filter-options`); query a `agenda/events`.
- “Sin consultorio” refleja el mismo set filtrado que el resto.
- Modal centrado + overlay; cierre Esc / overlay / Cerrar.
- Tests backend de filtros si faltan; nota runbook breve.

### Out of Scope

- Sync, mapeo id_agenda, ABM ubicaciones/consultorios.
- Cambios a `/agenda` o FullCalendar en otras pantallas.
- Filtro UI `id_dominio` aparte (queda Ubicación).
- Colores por tipo/dominio; drag&drop.

## Approach

Mantener grilla CSS. Unificar sistema de coordenadas (box-sizing / sin border que sume altura, o líneas absolutas también en HORA). Contenedor flex/altura `calc` con overflow interno. Cargar `GET .../filter-options`; enviar `tipo`/`especialidad`/`medico` repetidos. Reemplazar popover por modal con backdrop. Backend ya aplica filtros a unassigned — verificar y cubrir con test.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `frontend/src/pages/AgendaOcupacionPage.jsx` | Modified | Layout, filtros, modal, alineación |
| `backend/.../agenda_ocupacion.py` | Modified* | Solo si hace falta ajuste filtro unassigned |
| `backend/tests/test_agenda_ocupacion.py` | Modified | Filtros multi + unassigned |
| `docs/runbook.md` | Modified | Nota UI |

\* Preferir cero cambio API.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Multi-select con cientos de médicos | Med | Opciones desde filter-options; UI scrollable |
| `100vh` vs chrome del panel | Med | Medir offset header/filtros; flex column |
| Regresión alineación móvil | Low | Misma geometría; smoke visual |

## Rollback Plan

Revertir deploy frontend (y backend si hubo test-only / microfix). Sin migración.

## Dependencies

- Endpoints `agenda/events` y `agenda/filter-options` existentes.
- Survey `decisions.md` (Q1–Q4).

## Success Criteria

- [ ] Etiquetas de hora alineadas con líneas de fila en desktop.
- [ ] Grilla usa ancho panel + altura restante; scroll interno; columnas más anchas.
- [ ] Filtros multi tipo/especialidad/médico reducen eventos incl. Sin consultorio.
- [ ] Modal cierra con Esc, overlay y Cerrar.
- [ ] Tests filtros OK; runbook actualizado.
