# Tasks: Novedades (módulos)

## Phase 1: Datos y roles

- [x] 1.1 Alembic: extender enum `userrole` con `jefe_medico`, `rrhh`
- [x] 1.2 Alembic: tablas `novedades_*` (servicio, modulo, jefe_servicio, profesional_servicio, periodo, asignacion_modulo, novedad)
- [x] 1.3 Actualizar `models/user.py`, schemas users, `UsersPage.jsx` opciones de rol
- [x] 1.4 Guards en `deps.py`: `require_admin_or_rrhh`, `require_admin_or_jefe`, etc.

## Phase 2: Backend dominio

- [x] 2.1 Models + schemas Pydantic para maestros y cargas
- [x] 2.2 Services: ABM servicios/módulos; N:N jefe↔servicio; N:N profesional↔servicio
- [x] 2.3 Service período: un solo abierto; cerrar/reabrir (admin/rrhh)
- [x] 2.4 Period gate en create/update/delete de asignaciones y novedades
- [x] 2.5 Cargas: asignacion módulo + novedad (concepto FK, valor ARS, justificación required); scope jefe
- [x] 2.6 `ProfessionalDirectory` adaptando `professionals`
- [x] 2.7 Routers bajo `/api/v1/novedades/*` + registro en `main.py`
- [x] 2.8 Export XLS (`openpyxl`) con columnas/filtros acordados

## Phase 3: Frontend

- [x] 3.1 `navigation.js` + `NovedadesNavMenu` (roles); rutas en `main.jsx`
- [x] 3.2 Página Parametrización con tabs: servicios, módulos, jefes↔servicios, períodos
- [x] 3.3 Página Carga módulos: asignar módulos + cargar novedades (scope)
- [x] 3.4 Página Generación XLS: grilla, filtros, descarga (admin/rrhh)
- [x] 3.5 `ProtectedRoute` / helpers por rol en rutas Novedades
- [x] 3.6 Home: accesos rápidos Novedades según rol

## Phase 4: Tests y docs

- [x] 4.1 Tests RBAC: operador 403; jefe fuera de servicio 403; rrhh sin carga
- [x] 4.2 Tests período: segundo abierto falla; cerrado bloquea escritura; reopen OK
- [x] 4.3 Test validación justificación + export content-type
- [x] 4.4 Actualizar docs/runbook breve (roles + migrate) si aplica
- [ ] 4.5 Verificación manual checklist por rol

## Cierre

- [ ] Marcar verify; archivar change al merge
