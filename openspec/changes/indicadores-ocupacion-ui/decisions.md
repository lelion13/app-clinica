# Decisions: indicadores-ocupacion-ui

Survey closed 2026-10-03. Change: `indicadores-ocupacion-ui`. Branch: `indicadores-ocupacion-ui`.

| # | Topic | Choice | Decision |
|---|--------|--------|----------|
| Q1 | Control de período | A | Modo **Día \| Mes**: Día = date picker; Mes = selector año-mes. |
| Q2 | Cálculo en Mes | A | Misma fórmula que el día, agregada: horas sync mapeadas del mes ÷ horas `room_operating_hours` de todos los días del mes. |
| Q3 / Q3b | % en tops | A+B → A | Cada fila: **horas** + **% sobre box** (÷ denom torta) + **% sobre ocupado** (÷ numerador total). |
| Q4 | Tamaño/orden tops | B | Top **10**, orden por horas desc. |
| Q5 | Alcance filter-options | B | Cambiar `filter-options` compartido: especialidad = solo payload; médico = solo payload. Afecta también Agenda ocupación. |
| Q6 | Match al filtrar | A | Match estricto payload-only en Indicadores **y** Agenda (especialidad ≠ especialidad_agenda; médico = `medico_responsable_equipo` / legado `payload.medico`). |
| Q7 | Vacíos en tops | B | Agrupar como **“Sin especialidad”** / **“Sin médico”**. |

## Defaults (no preguntados)

- Torta: cada segmento/leyenda muestra **horas y %**.
- Tops usan `payload.especialidad` y `payload.medico_responsable_equipo` (misma fuente que filtros).
- Filtros ubicación/consultorio/especialidad/médico aplican al período activo (día o mes) y a torta + tops.
- Roles sin cambio: `admin` / `operador`.
