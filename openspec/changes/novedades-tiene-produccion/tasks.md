# Tasks: novedades-tiene-produccion

## 1. Backend

- [x] 1.1 Config `NOVEDADES_BONOS_TIENE_PRODUCCION_URL` (+ timeout opcional); token sync
- [x] 1.2 Service proxy httpx → parse boolean
- [x] 1.3 Router `GET /novedades/bonos/tiene-produccion` (admin/jefe)
- [x] 1.4 Tests: true/false parse, missing config, external fail

## 2. Frontend

- [x] 2.1 Helper check antes de submit en `NovedadesCargaPage`
- [x] 2.2 Mismo check al confirmar editar fecha (`CargasListGrid` / page wiring)
- [x] 2.3 Modales: sin producción (copy Q7) + error fail-closed

## 3. Docs

- [x] 3.1 `.env.example` / `.env.prod.example` + runbook
- [x] 3.2 Marcar tasks
