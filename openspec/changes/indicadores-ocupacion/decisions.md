# Decisions: indicadores-ocupacion

Survey CLOSED (2026-08-06).

| Q | Tema | Decisión |
|---|------|----------|
| Q1 | Definición % | **A** — Horas de bloques sync de agendas **mapeadas** al consultorio ÷ horas de `room_operating_hours` ese weekday |
| Q2 | Ventana | **A** — Un día (default hoy; date picker) |
| Q3 | Torta | **A** — Una torta **global** ocupado vs libre (+ leyenda / %) |
| Q4 | Rooms incluidos | **D** — Todos los consultorios creados (no borrados); sin ningún `id_agenda` → ocupación **0%** |
| Q5 | Sin horario ese weekday | **C** — Estado **“sin horario”**; fuera de la torta; aviso en UI |
| Q6 | Menú | **A** — Nueva opción **Indicadores ocupación** (convive con Estadística / bookings) |
| Q7 | Roles / path | **A** — `admin` + `operador`, `/indicadores-ocupacion` |
| Q8 | Filtros | **A1** — Selects de un valor (o Todos); AND. Especialidad/médico filtran **numerador**; denominador = horario de rooms incluidos por ubicación/consultorio |
| Q9 | Recorte / solapes | **C** — Contar bloque sync **completo** (no recortar al horario del box) |
| Q10 | % > 100% | **A** — Mostrar % real aunque supere 100% |

## Implícitos acordados

- Agendas **Sin consultorio** (`unassigned`) **no** suman al numerador de ningún room.
- Solo rooms con `deleted_at IS NULL`.
- Filtro ubicación: rooms de esa location (y `locations.tipo` ya está en el ABM; no se filtra por tipo aparte en v1 salvo vía location elegida).
- Especialidad: match `especialidad` **o** `especialidad_agenda` (mismo criterio que agenda ocupación).
- Change abierto `dashboard-estadisticas` (bookings) **no** se modifica en este change.
