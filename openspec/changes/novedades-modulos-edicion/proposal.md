# Proposal: novedades-modulos-edicion

## Intent

En Parametrización → Módulos: editar datos (+ flag `produccion`) y asociar/desasociar servicios vía modales separados; en Carga, si el módulo tiene `produccion=false`, omitir el check externo `tiene-produccion`.

## Scope

**In**
- Columna `produccion` (bool, default `false`) en `novedades_modulo`
- Create: checkbox `produccion` (default unchecked); create sigue exigiendo ≥1 servicio
- Modal **editar**: descripción, comentario, valor, `produccion` — Cancelar/Guardar
- Modal **servicios**: checkboxes (permite 0) — Cancelar/Aceptar
- API: `PUT /modulos/{id}` solo datos; `PUT /modulos/{id}/servicios` solo asociaciones
- Carga: skip check externo cuando hay módulo seleccionado con `produccion=false`
- Roles: admin/rrhh

**Out**
- Badge de producción en lista (Q8=B)
- Bloqueo al desasociar por historial (Q6=A)
- Branch nueva (Q10=B — misma branch)

## Approach

Migración + schemas; split update; UI dos modales; ajustar `NovedadesCargaPage` submit.

## Decisions

Ver `decisions.md` (Q1–Q10 closed).
