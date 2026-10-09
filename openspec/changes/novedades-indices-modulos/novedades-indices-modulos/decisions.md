# Decisions: novedades-indices-modulos

## Survey (closed)

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Orden menú Novedades | **A** — **Índices** al final |
| Q2 | Horas de módulos | Sin atributo estructurado → no calcular desde descripción |
| Q2c | Contador horas (este change) | **C** — solo horas de **novedades** |
| Q3 | Signo horas | **A** — neto: extras `+`, `horas_a_descontar` `−` |
| Q4 | Monto (inicial) | **C** — estilo CH (luego ajustado por Q11/Q12) |
| Q5 | Ajustes en monto | **A** — incluir (acotado por Q12 en por-servicio) |
| Q6 | Producción display | **C** — monto ARS **y** cantidad |
| Q7 | Módulos | **A** — cantidad de **asignaciones** (filas de carga) |
| Q8 | Profesionales (por servicio) | **A** — distintos con ≥1 carga (módulo o novedad) en ese servicio/período |
| Q9 | UI | **B** — dos secciones apiladas (servicio, luego profesional) |
| Q10 | Período | **A** — abierto o cerrado; sin período → sin datos / deshabilitado |
| Q11 | Producción por servicio | **A** — solo en panel por profesional (omitir / — en por servicio) |
| Q12 | Monto por servicio | **A** — cargas del servicio + ajustes con ese `servicio_id` (sin producción; sin ajustes `servicio_id` null) |
| Q13 | Export | **A** — solo pantalla |
| Q14 | Alcance producción | **A** — mismas reglas CH: bonos elegibles + prácticas + internaciones |
| Q15 | Nombre / ruta / rol | **A** — `novedades-indices-modulos`, menú **Índices**, `/novedades/indices`, solo **admin** |
| Q16 | Filas | **A** — solo con actividad en el período |
| Q17 | Orden | **A** — nombre A→Z |

## Derived metric matrix

### Por servicio (período seleccionado)
| Métrica | Definición |
|---------|------------|
| Horas | Σ horas novedades del servicio (neto por tipo) |
| Monto | Σ valor cargas (módulos+novedades) del servicio + Σ ajustes con ese `servicio_id` |
| Profesionales | count distinct `professional_id` con ≥1 carga en el servicio |
| Módulos | count asignaciones de módulo en el servicio |
| Producción | no aplica (columna omitida o —) |

### Por profesional (período seleccionado)
| Métrica | Definición |
|---------|------------|
| Horas | Σ horas novedades del profesional (neto; todos sus servicios) |
| Módulos | count asignaciones de módulo del profesional |
| Producción monto | ARS valorizado cuando exista en CH; en `feature/ocupacion` (CH solo cantidades de bonos) → **0** hasta tarifas/valorización en grilla |
| Producción cantidad | Σ cantidades de bonos del snapshot CH del período |

### Nota de rama
Implementado sobre `feature/ocupacion`: sin `horas_a_descontar` en enum (helper ya lo contempla si aparece); producción monto ARS queda en 0 alineado al CH qty-only de esta base.
