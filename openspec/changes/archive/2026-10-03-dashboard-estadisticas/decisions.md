# Decisions: dashboard-estadisticas

Documentación de cierre (proposal inicial + as-built).

| Tema | Decisión final |
|------|----------------|
| Menú / path | **Estadística** → `/estadisticas` |
| Roles | `admin` + `operador` |
| Ventana | Rango **desde–hasta** (máx. ~400 días en API) |
| Numerador | Horas de `room_weekly_assignments` proyectadas por ocurrencias de weekday en el rango (**no** bookings puntuales) |
| Denominador | Suma `room_operating_hours` en el rango para rooms filtrados |
| Filtros | Multi: ubicación, profesional, consultorio, especialidad; especialidad afecta numerador, no reduce capacidad |
| Visual | Torta ocupado/libre (capada a denom para pie) + barras weekday + top rooms/profesionales |
| Relación con Indicadores ocupación | Menús y APIs **separados**; fuentes distintas |
