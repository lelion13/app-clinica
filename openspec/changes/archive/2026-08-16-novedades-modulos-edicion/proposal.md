# Proposal: novedades-modulos-edicion

## Intent

En Parametrización → Módulos: editar datos (+ flag `produccion`), asociar/desasociar servicios, alta y baja vía modales; en Carga, si el módulo tiene `produccion=false`, omitir el check externo `tiene-produccion`.

## Scope

**In**
- Columna `produccion` (bool, default `false`) en `novedades_modulo` (Alembic `0018_modulo_produccion`)
- Alta: botón **Nuevo módulo** → modal (descripción, comentario, valor, `produccion`, servicios ≥1) con **Cancelar** / **Cargar** (`POST /modulos`)
- Modal **editar**: descripción, comentario, valor, `produccion` — Cancelar/Guardar
- Modal **servicios**: checkboxes (permite 0) — Cancelar/Aceptar → `PUT /modulos/{id}/servicios`
- Modal **eliminar**: resumen del módulo — Cancelar/Eliminar; Esc cancela
- API: `PUT /modulos/{id}` solo datos; `PUT /modulos/{id}/servicios` solo asociaciones (allow `[]`)
- Carga: skip check externo cuando hay módulo seleccionado con `produccion=false`
- Roles: admin/rrhh

**Out**
- Badge de producción en lista (Q8=B)
- Bloqueo al desasociar por historial (Q6=A)
- Branch nueva (Q10=B — misma branch que `tiene-produccion-force`)

## Approach

Migración + schemas; split update; UI modales en Param; ajustar `NovedadesCargaPage` submit.

## Decisions

Ver `decisions.md` (Q1–Q10 closed). Post-survey UX: alta y delete también en modal (`implementation-notes.md`).

## Depends on

`novedades-tiene-produccion` (proxy + force-load) — archivado el mismo día o antes; la interacción Q5=B asume ese comportamiento.
