# Design: distribucion-ocupacion

## Decisions

| Decisión | Rationale |
|----------|-----------|
| Proxy BFF live (sin DB) | Token server-side; v1 solo lectura; joins después |
| Reusar `NOVEDADES_PROF_SYNC_TOKEN` | Pedido explícito; misma API host |
| Env URL/timeout propios | Configurable sin redeploy de código |
| Prefijo `/api/v1/distribucion` | Separar de Novedades y maestros |
| Subset Pydantic | No filtrar payload completo al cliente más de lo necesario |

## Flow

```
Browser (JWT cookie) → GET /api/v1/distribucion/ocupacion/horarios-activos
  → httpx GET DISTRIBUCION_HORARIOS_ACTIVOS_URL + Bearer token
  → map subset → { items: [...] }
```

## API

- `GET /api/v1/distribucion/ocupacion/horarios-activos`
- Auth: cookie JWT + admin|operador
- 422 config / 502 upstream / 200 `{ items: HorarioActivoItem[] }`

## Files

- `backend/app/services/distribucion/horarios_activos.py`
- `backend/app/api/routers/distribucion.py`
- `backend/app/schemas/distribucion.py`
- `frontend/src/pages/OccupancyPage.jsx`

## Out of scope (deferred)

Persistencia, filtros, joins con consultorios/ubicaciones, cambios a Ocupación semanal.
