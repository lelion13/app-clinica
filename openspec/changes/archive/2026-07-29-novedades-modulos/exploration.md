# Exploration: Novedades (módulos / liquidación)

## Current State

- Roles reales: solo `admin` y `operador` (`UserRole` + enum PG + JWT claim `role`).
- No existen roles `jefe_medico` ni `rrhh`.
- Navegación: un dropdown “Distribución de consultorios” (`DistributionNavMenu` + `navigation.js`) + link Usuarios (admin).
- Dominio existente: ubicaciones, consultorios, profesionales (sync externo, UI read-only), reservas, ocupación, stats.
- No hay entidades `servicio`, `modulo`, `novedad`, `periodo` contable, ni export XLS/CSV.
- ABM tipico: router → service → schemas → soft delete; guards en `deps.py`.

## Affected Areas

- `backend/app/models/user.py` + Alembic — nuevos roles y tablas de dominio Novedades
- `backend/app/api/deps.py` — guards por rol (jefe médico / RRHH / admin)
- `frontend/src/config/navigation.js` + layout — sección “Novedades” tipo dropdown
- `frontend/src/pages/UsersPage.jsx` — alta/edición de roles nuevos
- Nuevos paquetes backend/frontend para módulos, servicios, períodos, cargas y export

## Approaches

1. **Dominio Novedades aislado** — tablas propias (servicio, modulo_catalogo, asociacion_jefe_servicio, periodo, novedad_carga) + mock de profesionales temporal.
   - Pros: no acopla a agenda/sync; migrable a MySQL/API después
   - Cons: dos fuentes de “profesional” hasta la integración
   - Effort: Medium–High

2. **Reusar `professionals` existente + mock seed** — mismas filas; Novedades referencia `professional_id`.
   - Pros: un solo maestro; UI combobox reutilizable
   - Cons: sync real puede pisar/mezclar mocks; filtrado por “servicio” no existe hoy
   - Effort: Medium

## Recommendation

Approach **1** con FK opcional a `professionals.id` cuando exista match, y tabla/mock `novedades_professionals` (o flag) hasta la API MySQL. Survey de producto debe cerrar definición de módulo vs novedad, período y RBAC.

## Risks

- Enum PG `userrole`: migración de valores nuevos es delicada
- Ambigüedad “módulo cargado” vs “novedad con concepto/valor/justificación”
- Cierre de período debe bloquear escrituras en API (no solo UI)
- Export XLS sin librería previa en el stack

## Ready for Proposal

Survey **cerrada** (2026-07-28). Proposal/spec/design/tasks listos. Implementar solo cuando el owner lance apply.
