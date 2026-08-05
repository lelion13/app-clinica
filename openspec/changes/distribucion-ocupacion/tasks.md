# Tasks: distribucion-ocupacion

## Phase 1 — Backend

- [x] 1.1 Config `DISTRIBUCION_HORARIOS_ACTIVOS_URL` / `TIMEOUT`
- [x] 1.2 Schema `HorarioActivoItem` + response
- [x] 1.3 Service httpx proxy (422/502)
- [x] 1.4 Router `GET /ocupacion/horarios-activos` + include en `main.py`
- [x] 1.5 Tests unitarios del servicio
- [x] 1.6 Tabla `ocupacion_horario_activo` + alembic `0011`
- [x] 1.7 Sync wipe+reload (`POST .../sync`); GET lista desde DB con filtro vigencia

## Phase 2 — Frontend

- [x] 2.1 Ítem menú Ocupación `/ocupacion`
- [x] 2.2 Ruta en `main.jsx`
- [x] 2.3 `OccupancyPage` grilla + auto-load + Actualizar
- [x] 2.4 Multi-select filtros por columna + Limpiar filtros
- [x] 2.5 Botón Indicadores (modal) agrupado id_dominio+especialidad+medico+dia
- [x] 2.6 Actualizar = sync + recarga; carga inicial solo DB

## Phase 3 — Ops / docs

- [x] 3.1 `.env.example` + `.env.prod.example`
- [x] 3.2 Runbook
- [x] 3.3 Spec / design / proposal (SDD)

## Phase 4 — Ubicación ↔ id_dominio

- [x] 4.1 Alembic `0014_locations_id_dominio` (placeholder −id, unique parcial activas)
- [x] 4.2 Model/schemas/service/router con `id_dominio` obligatorio (>0)
- [x] 4.3 UI Ubicaciones: alta con id_dominio + editar nombre/id_dominio
