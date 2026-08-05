# Decisions — agenda-ocupacion-sync

**Estado:** SURVEY CLOSED  
**Change:** `agenda-ocupacion-sync`  
**Branch:** `feature/ocupacion` (o nueva feature branch al implement)

| # | Tema | Decisión |
|---|------|----------|
| Q1 | Relación con Agenda actual | **C** — Menú nuevo; `/agenda` intacta |
| Q2 | Materialización en calendario | **B** — Bloques en ventana visible (datesSet) |
| Q3 | Qué filas entran | **B** — Solape `[fecha_desde, fecha_hasta]` con ventana |
| Q4 | Filtros | **A+B+C+D+E** — dominio, tipo, especialidad(es), médico, día |
| Q5 | Título del bloque | **E** — solo `medico`; click = detalle |
| Q6 | Interacción | **A** — solo lectura |
| Q7 | Menú / ruta | **A** — Agenda ocupación `/agenda-ocupacion` |
| Q8 | Sync | **A** — solo lee DB; sync desde Ocupación |
| Q9 | Roles | **A** — admin + operador |
| Q10 | Color | **A** — un solo color |
| Q11 | Filtro especialidad | **D** — matchea especialidad O especialidad_agenda |
| Q12 | Sin `dia` | **A** — excluir del calendario |
| Q13 | Detalle al click | **B** — Popover/tooltip junto al bloque |
| Q14 | Label id_dominio | **C** — solo nombre ubicación; si no hay match, el número |
| Q15 | Materialización | **B** — Backend `GET .../events?start=&end=` (+ filtros) |

## Notas
- Sync mandante sigue en pantalla Ocupación; esta vista solo lee snapshot DB.
- Performance: B evita bajar ~7k filas al browser.
