# Implementation notes — dashboard-estadisticas

## As-built vs proposal

| Proposal v1 | Implementado |
|-------------|--------------|
| Numerador = bookings | Numerador = `room_weekly_assignments` proyectadas al rango |
| — | Filtro especialidad sobre profesionales de esas asignaciones |

## Anti-ambigüedad

No confundir con **Indicadores ocupación** (`/indicadores-ocupacion`, sync externo, un día).
