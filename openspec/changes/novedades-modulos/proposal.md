# Proposal: Sección Novedades (módulos)

## Intent

Agregar menú **Novedades** (dropdown) para asignar módulos y cargar novedades por servicio, parametrizar catálogo/asociaciones/períodos, y permitir a RRHH/admin grilla + export XLS con bloqueo por período cerrado.

## Scope

### In Scope
- Nav **Novedades**: Carga módulos, Generación XLS, Parametrización (pestañas).
- Roles `jefe_medico` y `rrhh`; matriz en `decisions.md`.
- ABM servicios, módulos, asociaciones jefe↔servicio (N:N), períodos.
- Asignación de módulos a profesionales; carga de novedades (concepto=módulo, valor ARS, justificación obligatoria).
- Grilla + búsqueda + XLS; cierre/reapertura de período.
- Profesionales vía adaptador sobre `professionals` (swappeable).

### Out of Scope
- MySQL/API real de profesionales; liquidación; PDF; emails; cambios a agenda salvo roles/nav.

## Approach

Dominio Novedades en PostgreSQL + Alembic; guards JWT por rol; export openpyxl; soft-delete; un solo período abierto.

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/app/models/user.py` + Alembic | Roles + tablas Novedades |
| `backend/app/api/deps.py` | Guards |
| `backend/app/**` novedades | New API |
| `frontend` navigation + páginas | Sección Novedades |
| `UsersPage.jsx` | Roles nuevos |

## Risks

| Risk | Mitigation |
|------|------------|
| Enum PG roles | Migración Alembic + tests |
| Período solo UI | Validar en service |
| Origen profesionales | Puerto/adaptador |

## Rollback

Revert migración/código; ocultar nav Novedades.

## Success Criteria

- [ ] Jefe/admin carga solo en sus servicios y período abierto
- [ ] Período cerrado bloquea escritura (cualquier rol)
- [ ] RRHH/admin grilla + XLS; ABM param
- [ ] Justificación obligatoria; concepto FK módulo

**Estado:** survey cerrada — listo para spec/design/tasks.
