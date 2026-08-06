# Proposal: locations.tipo + vínculo ocupación (retroactivo)

## Intent

Documentar e historiar el cambio ya implementado: cada ubicación se vincula a ocupación por el par `(id_dominio, tipo)`, con `tipo` obligatorio — porque un dominio puede tener varios tipos/sedes.

## Scope

### In Scope (hecho en código)

- Migración `0016_locations_tipo`.
- Model/schemas/service/router + UI Ubicaciones.
- Agenda ocupación: filtro ubicación = dominio + tipo; labels por par.
- Tests schemas + filtro agenda; nota runbook.

### Out of Scope

- Auto-importar ubicaciones desde sync.
- Multi-tipo por una sola fila location.

## Approach

Unique parcial activa `(id_dominio, tipo)`. Placeholders `PENDIENTE-{id}` en migrate. UI exige tipo al crear/editar. Backend agenda ya filtraba por location_id; se endureció match de tipo.

## Affected Areas

| Area | Impact |
|------|--------|
| `backend/alembic/versions/0016_locations_tipo.py` | New |
| `backend/app/models/location.py` | Mod |
| `backend/app/schemas/location.py` | Mod |
| `backend/app/services/location_service.py` | Mod |
| `backend/app/.../agenda_ocupacion.py` | Mod |
| `frontend/.../LocationsPage.jsx` | Mod |
| `docs/runbook.md` | Mod |

## Risks

| Risk | Mitigation |
|------|------------|
| Placeholders no editados | UI marca pendiente; filtro agenda no matchea tipo real |
| Case mismatch tipo | Match agenda con `casefold` |

## Rollback

Downgrade `0016` (pierde tipo); revertir código. Preferible corregir datos en UI.

## Success Criteria

- [x] Unique `(id_dominio, tipo)` entre activas
- [x] tipo obligatorio create/update
- [x] Agenda filtra por dominio+tipo de la location
- [x] Runbook menciona 0016

## Nota proceso

Implementado **antes** de abrir este change SDD (follow-up de ocupación). Carpeta creada para cerrar la deuda documental.
