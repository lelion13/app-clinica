# Decisions: indicadores-turnos-csv

Survey closed 2026-10-05. Change: `indicadores-turnos-csv`. Branch: `agenda-ocupacion-dnd` (mismo branch de trabajo).

| # | Topic | Choice | Decision |
|---|--------|--------|----------|
| Q1 | Cantidad turnos | C | Solo estados **AT + AU**. CA/PR/EE fuera. |
| Q2 | Ausentes | A | Solo **AU**. |
| Q3 | Match Nombre | A | Exacto **normalizado** (trim + casefold; sin acentos). |
| Q4 | Persistencia | User | DB; asociado a **nombre de archivo** + **período del CSV**. |
| Q5 | Período CSV | B | Por rango real de **Fecha Turno** (min–max). |
| Q6 | Filtro período UI | A | Solo filas con Fecha Turno en el Día/Mes activo de Indicadores. |
| Q7 | Filtros ubicación/etc. | A | Tras match, atributos del **sistema** (agenda sync + mapeo room). |
| Q8 | Promedios tiempo | A | Solo **AT** con fechas completas (presente→atención; reserva→turno). |
| Q9 | Sin match | B | **Bloquea** el import; modal lista filas/nombres sin match. |
| Q10 | Re-import mismo período | B | **Suma** (pueden coexistir varios archivos). |

## Defaults

- Ausentismo % = AU / (AT+AU) × 100 (mismo conjunto Q1).
- Espera en **días**; presente→atendido en **minutos**.
- Roles `admin`|`operador`.
