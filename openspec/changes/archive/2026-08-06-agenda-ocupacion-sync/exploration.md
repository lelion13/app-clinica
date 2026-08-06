# Exploration: agenda-ocupacion-sync

## Goal

Visualizar en calendario (FullCalendar) el snapshot sync `ocupacion_horario_activo`, con filtros, sin tocar Agenda de bookings.

## Context

- Datos ya persistidos (~7k filas); sync mandante en `/ocupacion`.
- Agenda actual `/agenda` = bookings; survey Q1=C → menú nuevo.
- `locations.id_dominio` permite label de ubicación.

## Approaches

| # | Approach | Pros | Cons |
|---|----------|------|------|
| 1 | Frontend materializa 7k | Simple | Pesado en red/CPU |
| 2 | Backend events?start&end | Payload chico | Más lógica backend |
| 3 | Híbrido filtro fechas + FC client | Balance | Dos sitios con reglas |

**Elegido:** #2 (Q15=B).

## Risks

- Mapeo `dia` español → weekday; filas sin dia excluidas (Q12).
- Solapes visuales densos → un color + popover (Q10/Q13).
