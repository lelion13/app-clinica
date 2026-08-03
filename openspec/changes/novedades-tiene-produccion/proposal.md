# Proposal: Control tiene-producción en Carga

## Intent

Cuando admin/jefe intenta cargar módulo/novedad o editar la fecha de realización, verificar contra producción externa (`/bonos/tiene-produccion?fecha&codprof`). Si `false`, mostrar modal y no permitir la operación. Si el API falla, también bloquear.

## Scope

### In Scope

- Proxy backend (token no en browser): `GET` app → externo con Bearer sync.
- Env `NOVEDADES_BONOS_TIENE_PRODUCCION_URL` (default documentado).
- UI Carga: check al pulsar Cargar (antes del POST); `codprof` del catálogo; fecha = fecha realización.
- UI editar fecha en listado de Carga: mismo check antes de confirmar.
- Roles: admin y jefe_medico.
- Modal copy fijo cuando `false`; fail-closed si error de red/API.
- Tests proxy + docs/runbook/env example.

### Out of Scope

- Revalidación obligatoria en endpoints de create/update del backend (Q1=A).
- RRHH / Capital Humano.
- Cache persistente del resultado.

## Approach

1. Config + service httpx similar a bonos.
2. Endpoint JWT protegido p.ej. `GET /novedades/bonos/tiene-produccion?fecha=&codprof=` → `{ "tiene_produccion": bool }`.
3. Front: helper `assertTieneProduccion` antes de submit alta y antes de update fecha.

## Risks

| Risk | Mitigation |
|------|------------|
| Token en browser | Solo proxy (Q4b) |
| Bypass API create | Aceptado Q1=A; documentar |
| API lento al cargar | Spinner en botón; fail-closed |

## Rollback

Revert deploy; quitar check UI + endpoint proxy.

## Success Criteria

- `false` → modal A y no POST.
- Error API → no POST.
- `true` → flujo actual.
- Editar fecha respeta la misma regla.
