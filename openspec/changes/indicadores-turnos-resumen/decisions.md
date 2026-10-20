# Decisions: indicadores-turnos-resumen

| ID | Tema | Decisión |
|----|------|----------|
| D1 | Nombre | `indicadores-turnos-resumen` |
| D2 | Env URL | `DISTRIBUCION_TURNOS_RESUMEN_URL` |
| D3 | Auth | Bearer `NOVEDADES_PROF_SYNC_TOKEN` |
| D4 | Día | `fecha_desde` = `fecha_hasta` = fecha selector |
| D5 | Mes | 1º–último día del mes; una llamada |
| D6 | Join | `turno_horario_id` = `id` ocupación |
| D7 | Filtros | Solo reclasifican en memoria el set ya bajado |
| D8 | Fetch | Solo al cambiar día/mes (o al montar con ese período) |
| D9 | UI métricas | Todos los campos del JSON (agregados) |
| D10 | Agregación | Σ contadores; % desde totales; `espera_promedio_dias` ponderado por `total_turnos` |
| D11 | Ocupación | Columna `id` visible |
| D12 | Errores | No bloquean torta/KPIs/CSV; aviso en el bloque |
| D13 | Proxy | Solo backend (token no al cliente) |
