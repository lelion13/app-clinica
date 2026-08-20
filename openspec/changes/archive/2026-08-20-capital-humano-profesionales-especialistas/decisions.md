# Decisions: capital-humano-profesionales-especialistas

Survey: **una pregunta a la vez**. Estado: **CLOSED** (2026-08-20).

## Acuerdos previos (fuera de survey)

- Endpoint propio: `NOVEDADES_PROF_ESPECIALISTAS_URL`
- Token: `NOVEDADES_PROF_SYNC_TOKEN`
- Persistencia en sync (no en Actualizar de CH)
- Campo en `novedades_profesional` (`es_especialista`)
- Post-sync (Param): modal con `profesional` + `descripcion` no matcheados a catálogo

## Decisiones

| # | Tema | Decisión | Notas |
|---|------|----------|-------|
| Q1 | Alcance del +20% | **A** | Solo módulos asignados (no novedades) |
| Q2 | Dónde se aplica el plus | **A** | Al cargar el módulo: persistir `valor = valor_módulo × 1.20` si especialista; CH solo suma lo guardado |
| Q3 | UI sync + modal | **B** | Fetch especialistas solo en sync de Parametrización; modal de no matcheados ahí. Mis profesionales sync sin especialistas |
| Q4 | Fallo API especialistas | **C** | Catálogo sync OK; flags no se tocan + aviso del fallo |
| Q5 | Visibilidad del flag | **D** | En Capital Humano, al abrir **Detalle**, indicar si el profesional es especialista |

## Implicaciones

- Cargas históricas de módulo **sin** plus no se recalculan solas; el plus aplica a **nuevas** cargas de módulo tras marcar especialista.
- Mis profesionales: sync de listado sin tocar especialistas.
- Response de sync Param debe incluir `especialistas_unmatched: [{profesional, descripcion}]` y/o error parcial de especialistas.
