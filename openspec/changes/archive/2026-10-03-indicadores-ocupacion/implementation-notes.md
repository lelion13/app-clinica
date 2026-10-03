# Implementation notes — indicadores-ocupacion

## Entregado

| Pieza | Path |
|-------|------|
| Service | `backend/app/services/distribucion/indicadores_ocupacion.py` |
| Schemas | `IndicadoresOcupacionResponse` en `schemas/distribucion.py` |
| Router | `GET .../ocupacion/indicadores` |
| UI | `frontend/src/pages/IndicadoresOcupacionPage.jsx` |
| Nav | `Indicadores ocupación` → `/indicadores-ocupacion` |
| Tests | `backend/tests/test_indicadores_ocupacion.py` |

## Anti-ambigüedad vs Estadística

| | Indicadores ocupación | Estadística |
|--|----------------------|-------------|
| Fuente numerador | Sync `ocupacion_horario_activo` + mapeo `id_agenda` | Asignaciones semanales (`room_weekly_assignments`) proyectadas al rango |
| Ventana | Un día | Rango desde–hasta |
| Path | `/indicadores-ocupacion` | `/estadisticas` |

## Ops

Sin migración. Deploy backend+frontend. Requiere sync + mapeos + horarios de box.
