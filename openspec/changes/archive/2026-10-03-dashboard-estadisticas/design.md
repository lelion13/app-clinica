# Design: dashboard-estadisticas (as-built)

## Approach

`stats_service.build_stats_summary` + router `stats.py` + `EstadisticasPage` (recharts).

## Key files

| Path | Rol |
|------|-----|
| `backend/app/services/stats_service.py` | Cálculo enabled / assigned hours |
| `backend/app/api/routers/stats.py` | `GET /stats/summary` |
| `backend/app/schemas/stats.py` | Response |
| `frontend/src/pages/EstadisticasPage.jsx` | UI |
| `frontend/src/config/navigation.js` | Ítem Estadística |

## Note

Proposal mencionaba bookings; código usa weekly assignments. Spec estable documenta el as-built.
