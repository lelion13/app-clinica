# Design: distribucion-ocupacion

## Decisions

| Decisión | Rationale |
|----------|-----------|
| Snapshot DB + wipe/reload transaccional | Endpoint mandante; sin fantasmas ni datos a medias si falla el GET |
| GET lista DB; POST sync en Actualizar | Carga rápida; sync explícito |
| Reusar `NOVEDADES_PROF_SYNC_TOKEN` | Pedido explícito |
| PK `id_dato` | Clave natural del payload |
| Persistir todos los campos + split nombre | Q26/Q28 |

## Flow

```
Carga:  Browser → GET .../horarios-activos → SELECT DB → filter fecha_hasta>=hoy
Actualizar: Browser → POST .../sync → httpx GET externo → DELETE ALL + INSERT (txn) → GET lista
```

## API

- `GET /api/v1/distribucion/ocupacion/horarios-activos` → DB vigente
- `POST /api/v1/distribucion/ocupacion/horarios-activos/sync` → wipe+reload
- Auth: JWT + admin|operador

## Files

- `backend/app/services/distribucion/horarios_activos.py`
- `backend/app/api/routers/distribucion.py`
- `backend/app/schemas/distribucion.py`
- `frontend/src/pages/OccupancyPage.jsx`

## Out of scope (deferred)

Persistencia, filtros, joins con consultorios/ubicaciones, cambios a Ocupación semanal.
