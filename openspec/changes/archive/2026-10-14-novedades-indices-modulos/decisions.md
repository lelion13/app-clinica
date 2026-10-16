# Decisions: novedades-indices-modulos

## Survey (closed) — Índices UI

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Orden menú Novedades | **A** — **Índices** al final |
| Q2 (histórico) | Horas de módulos | Sin atributo → no parsear descripción (**superseded** por survey módulo.horas) |
| Q2c (histórico) | Contador horas | Solo novedades (**superseded**: ahora módulo + novedades) |
| Q3 | Signo horas novedades | **A** — neto: extras `+`, `horas_a_descontar` `−` |
| Q4 | Monto (inicial) | **C** — estilo CH (luego ajustado por Q11/Q12) |
| Q5 | Ajustes en monto | **A** — incluir (acotado por Q12 en por-servicio) |
| Q6 | Producción display | **C** — monto ARS **y** cantidad |
| Q7 | Módulos | **A** — cantidad de **asignaciones** (filas de carga) |
| Q8 | Profesionales (por servicio) | **A** — distintos con ≥1 carga (módulo o novedad) en ese servicio/período |
| Q9 | UI | **B** — dos secciones apiladas (servicio, luego profesional) |
| Q10 | Período | **A** — abierto o cerrado; sin período → sin datos / deshabilitado |
| Q11 | Producción por servicio | **A** — solo en panel por profesional (omitir / — en por servicio) |
| Q12 | Monto por servicio | **A** — cargas del servicio + ajustes con ese `servicio_id` (sin producción; sin ajustes `servicio_id` null) |
| Q13 | Export Índices | **A** — solo pantalla |
| Q14 | Alcance producción | **A** — mismas reglas CH: bonos elegibles + prácticas + internaciones |
| Q15 | Nombre / ruta / rol | **A** — `novedades-indices-modulos`, menú **Índices**, `/novedades/indices`, solo **admin** |
| Q16 | Filas | **A** — solo con actividad en el período |
| Q17 | Orden | **A** — nombre A→Z |

## Survey (closed) — `módulo.horas` (catálogo)

| # | Topic | Choice |
|---|--------|--------|
| H1 | Alta (Nuevo módulo) | **B** — `horas` **obligatorio** también en alta |
| H2 | Tipo / rango | **A** — entero ≥ 1 |
| H3 | Índices | **A** — Horas = Σ (`módulo.horas` por asignación) + horas netas novedades |
| H4 | NULL legacy en Índices | **A** — cuenta **0** horas de módulo; novedades siguen |
| H5 | Import Excel módulos | **C** — out of scope (solo ABM Parametrización alta/edición) |

## Derived metric matrix

### Por servicio (período seleccionado)
| Métrica | Definición |
|---------|------------|
| Horas | Σ `módulo.horas` de cada asignación (NULL → 0) **+** Σ horas novedades netas del servicio |
| Monto | Σ valor cargas (módulos+novedades) del servicio + Σ ajustes con ese `servicio_id` |
| Profesionales | count distinct `professional_id` con ≥1 carga en el servicio |
| Módulos | count asignaciones de módulo en el servicio |
| Producción | no aplica (columna omitida o —) |

### Por profesional (período seleccionado)
| Métrica | Definición |
|---------|------------|
| Horas | Σ `módulo.horas` de sus asignaciones (NULL → 0) **+** Σ horas novedades netas |
| Módulos | count asignaciones de módulo del profesional |
| Producción monto | igual CH (`monto_bonos`: bonos elegibles + prácticas + internaciones valorizados) |
| Producción cantidad | Σ cantidades de esos mismos ítems elegibles |

### Catálogo módulo.`horas`
- Migración: columna nullable; existentes = NULL.
- Create/Update API+UI: requerido, entero ≥ 1 (422 si falta/ inválido).
- Import Excel módulos: no cambia en este change.

### Nota de rama
Implementación en **`feature/novedades-indices-modulos`** (desde `origin/master`).
