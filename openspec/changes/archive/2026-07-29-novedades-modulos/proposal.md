# Proposal: Sección Novedades (módulos)

## Intent

Agregar menú **Novedades** (dropdown) para asignar módulos y cargar novedades por servicio, parametrizar catálogo/asociaciones/períodos, y permitir a RRHH/admin grilla + export XLS con bloqueo por período cerrado.

## Scope

### In Scope
- Nav **Novedades**: Carga módulos, Generación XLS, Parametrización (pestañas).
- Roles `jefe_medico` y `rrhh`; matriz en `decisions.md`.
- ABM servicios (**valor hora**), módulos (**N:N con servicios**), asociaciones jefe↔servicio y profesional↔servicio, períodos.
- Asignación de módulos a profesionales (valor catálogo solo lectura).
- Carga de novedades: **tipo** (hora extra / hora extra por ausencia) + **horas** enteras; valor = horas × valor hora del servicio.
- Listado en Carga: grilla unificada, alcance por servicios del jefe, filtro/sort, modal de anulación.
- Grilla + búsqueda + XLS (admin/rrhh); cierre/reapertura de período.
- Profesionales vía adaptador sobre `professionals` (swappeable).

### Out of Scope
- MySQL/API real de profesionales; liquidación; PDF; emails; cambios a agenda salvo roles/nav.

## Approach

Dominio Novedades en PostgreSQL + Alembic (`0004`–`0006`); guards JWT por rol; export openpyxl; soft-delete; un solo período abierto.

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/app/models/user.py` + Alembic | Roles + tablas Novedades |
| `backend/app/api/deps.py` | Guards |
| `backend/app/**` novedades | New API |
| `frontend` navigation + páginas | Sección Novedades |
| `UsersPage.jsx` | Roles nuevos |
| `docs/runbook.md` | Operación / migrate |

## Risks

| Risk | Mitigation |
|------|------------|
| Enum PG roles | Migración Alembic + tests |
| Período solo UI | Validar en service |
| Origen profesionales | Puerto/adaptador |
| `alembic_version` VARCHAR(32) | Revision ids cortos (`0006_mod_svc_valor_hora`) |

## Rollback

Revert migración/código; ocultar nav Novedades.

## Success Criteria

- [x] Jefe/admin carga solo en sus servicios y período abierto
- [x] Período cerrado bloquea escritura (cualquier rol)
- [x] RRHH/admin grilla + XLS; ABM param
- [x] Novedad = tipo + horas; valor = horas × valor_hora servicio
- [x] Jefe ve solo cargas de sus servicios; grilla ordenable/filtrable; modal anular

**Estado:** implementado en código; docs del change sincronizadas (2026-07-29). Pendiente verify/archive al merge.
