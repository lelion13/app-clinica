# Decisions: limpiar-ui-obsoleta

| ID | Tema | Decisión |
|----|------|----------|
| D1 | Scope UI | Eliminar menú + páginas + rutas de Ocupación semanal, Agenda (bookings), Estadística. |
| D2 | No tocar | Ocupación `/ocupacion`, Agenda ocupación, Indicadores ocupación, Ubicaciones, Profesionales, Consultorios. |
| D3 | APIs | Eliminar solo si el uso es exclusivo de lo removido (`/bookings`, `/weekly-assignments`, `/stats`). |
| D4 | DB | Drop tablas exclusivas (`bookings`, `room_weekly_assignments` u equivalentes) tras grep; no drop `professionals` / rooms / hours. |
| D5 | URLs viejas | Redirect permanente a Home (`/`). |
| D6 | Profesionales | Se queda en este change. |
| D7 | Backup | Operador hace backup antes de actualizar; no soft-drop en migración. |
| D8 | Consumidores | Solo esta app web. |
| D9 | Nombre | `limpiar-ui-obsoleta`. |
