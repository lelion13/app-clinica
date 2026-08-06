# Tasks: Indicadores ocupación

## Phase 1 — Backend cálculo

- [x] 1.1 Schemas response indicadores (horas, %, rooms_without_hours, …)
- [x] 1.2 Service `indicadores_ocupacion.py`: rooms, operating hours, mapeo, bloques sync día, filtros
- [x] 1.3 Router `GET .../ocupacion/indicadores` (JWT admin|operador)
- [x] 1.4 Tests: sin agenda, sin horario, % >100, filtro médico no reduce denom

## Phase 2 — Frontend

- [x] 2.1 Nav **Indicadores ocupación** + ruta `/indicadores-ocupacion`
- [x] 2.2 Página: filtros fecha/ubicación/consultorio/especialidad/médico (selects)
- [x] 2.3 Torta recharts + KPI %/horas + lista sin horario
- [x] 2.4 Carga al abrir (hoy, sin filtros)

## Phase 3 — Docs / verify

- [x] 3.1 Runbook breve
- [ ] 3.2 Smoke: menú, torta, filtros, Estadística intacta
- [ ] 3.3 (Opcional) nota en `openspec/specs/distribucion` al archivar

## Notes

- No tocar `stats_service` / `EstadisticasPage` / change `dashboard-estadisticas`.
- No sync desde esta pantalla.
