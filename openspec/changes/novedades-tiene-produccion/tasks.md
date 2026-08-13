# Tasks: novedades-tiene-produccion

## 1. Backend (v1) — hecho

- [x] 1.1 Config `NOVEDADES_BONOS_TIENE_PRODUCCION_URL` (+ timeout opcional); token sync
- [x] 1.2 Service proxy httpx → parse boolean
- [x] 1.3 Router `GET /novedades/bonos/tiene-produccion` (admin/jefe)
- [x] 1.4 Tests: true/false parse, missing config, external fail

## 2. Frontend (v1) — hecho

- [x] 2.1 Helper check antes de submit en `NovedadesCargaPage`
- [x] 2.2 Mismo check al confirmar editar fecha (`CargasListGrid` / page wiring)
- [x] 2.3 Modales: sin producción (copy Q7) + error fail-closed

## 3. Docs (v1) — hecho

- [x] 3.1 `.env.example` / `.env.prod.example` + runbook
- [x] 3.2 Marcar tasks

## 4. Backend (v2 — force load)

- [x] 4.1 Alembic: `motivo_sin_produccion` + `observacion_sin_produccion` en asignación y novedad
- [x] 4.2 Models + create/update schemas + responses
- [x] 4.3 Validar enum/obs si vienen en create; persistir; listados exponen campos
- [x] 4.4 Tests create con/sin motivo

## 5. Frontend (v2)

- [x] 5.1 Modal force: mensaje + combo (Vacaciones/Enfermedad, default vacío) + observación
- [x] 5.2 Cancelar cierra sin POST; Cargar valida y POST con campos en módulo y/o novedad
- [x] 5.3 Error API sigue modal simple (sin force); editar fecha sin force
- [x] 5.4 Mostrar motivo/obs en grilla Carga (columna o detalle)

## 6. Docs (v2)

- [x] 6.1 Runbook breve + marcar tasks v2
