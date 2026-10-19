# Exploration: limpiar-ui-obsoleta

## Goal

Quitar del producto tres capacidades obsoletas bajo Distribución, sin romper Ocupación / Agenda ocupación / Indicadores / Profesionales / resto.

## Remove (confirmed)

| UI | Path | API primaria | Datos |
|----|------|--------------|-------|
| Ocupación semanal | `/ocupacion-semanal` | `/weekly-assignments` | `room_weekly_assignments` |
| Agenda (reservas) | `/agenda` | `/bookings` | `bookings` |
| Estadística | `/estadisticas` | `/stats` | solo lee weekly assignments + hours |

## Keep

- `/ocupacion`, `/agenda-ocupacion`, `/indicadores-ocupacion`, `/ubicaciones`, `/profesionales`, `/consultorios`, Novedades, Usuarios, Config.

## Q&A

| Q | Decisión |
|---|----------|
| Q1 | Eliminar menú + pantallas + rutas + APIs exclusivas |
| Q2 | Paths confirmados; no tocar sync Ocupación / Agenda ocupación / Indicadores |
| Q3 | Drop tablas/datos si no se usan en otro lado |
| Q4 | URLs viejas → redirect a Home |
| Q5 | Change name = `limpiar-ui-obsoleta` |
| Q6 | Profesionales se queda (posible change futuro) |
| Q7 | Backup lo hace el operador antes de actualizar |
| Q8 | APIs solo consumidas por esta app |

## Dependency check (preliminar)

- `stats` → solo `RoomWeeklyAssignment` + `room_operating_hours` (hours se quedan).
- `bookings` → solo AgendaPage (+ FK professionals/rooms; no borrar esas tablas).
- `weekly-assignments` → WeeklyOccupancyPage + stats.
- `/professionals` → **NO** eliminar (Profesionales UI).
- `/consulting-rooms`, hours, locations, distribucion ocupacion/* → **NO** eliminar.
