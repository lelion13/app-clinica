# Proposal: Agenda ocupación — mejora UI visual

## Intent

Mejorar legibilidad y usabilidad de `/agenda-ocupacion`: alineación hora↔filas, grilla dominante en el viewport, filtros compactos que reduzcan ruido (incl. Sin consultorio), modal de detalle cerrable con Esc/overlay.

## Scope

### In Scope

- Fix alineación vertical HORA ↔ celdas.
- Layout Q1=C: full-bleed, altura viewport, scroll interno, header sticky, columnas ≥160px.
- Filtros UI en **una fila**: selects (como Ubicación) para tipo / especialidad / médico + ubicación + día; opciones vía `filter-options`.
- Sin consultorio respeta los mismos filtros.
- Modal centrado + overlay; Esc / overlay / Cerrar.
- Tests backend de filtros; runbook; `implementation-notes.md`.

### Out of Scope

- Sync, mapeo id_agenda, ABM ubicaciones (ver change `locations-tipo`).
- Cambios a `/agenda` / FullCalendar en otras pantallas.
- Multi-select de filtros (descartado post-survey por UX).
- Colores por tipo; drag&drop.

## Approach

Grilla CSS. Coordenadas verticales unificadas (absolute + border-box). Contenedor flex/`100dvh`. Selects de un valor → query `tipo`/`especialidad`/`medico` (API sigue aceptando listas). Modal con backdrop. Prioridad visual: **maximizar grilla**.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `frontend/src/pages/AgendaOcupacionPage.jsx` | Modified | Layout, filtros, modal, alineación |
| `backend/tests/test_agenda_ocupacion.py` | Modified | Filtros unassigned |
| `docs/runbook.md` | Modified | Nota UI |
| `openspec/changes/agenda-ocupacion-ui/*` | Modified | Artefactos + notes |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Muchas opciones en select médico | Med | select nativo con scroll; vacío = Todos |
| Offset `100dvh` vs header | Med | Ajuste ~112px; smoke |
| Front deploy sin back | Low | Filtros usan API ya existente |

## Rollback Plan

Revertir deploy frontend. Sin migración en este change.

## Dependencies

- `agenda/events` + `filter-options`.
- Preferible: `locations-tipo` (0016) en prod para filtro ubicación correcto.
- Survey `decisions.md`.

## Success Criteria

- [x] Horas alineadas con filas (código)
- [x] Viewport + sticky + columnas anchas
- [x] Filtros en una fila (selects) — ajuste post-survey
- [x] Modal Esc/overlay
- [x] Tests + runbook + implementation-notes
- [ ] Smoke en VPS con UI final
