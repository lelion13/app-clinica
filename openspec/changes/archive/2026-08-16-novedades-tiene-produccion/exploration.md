# Exploration: novedades-tiene-produccion

## Topic

Antes de cargar módulo/novedad (o editar fecha) en Carga, consultar si el profesional tiene producción ese día vía API externo `tiene-produccion`.

## Current State

- Carga: form con período, servicio, `fecha_realizacion`, profesional (typeahead con `codprof`), módulo y/o novedad.
- Editar fecha: modal en grilla inferior (`CargasListGrid`).
- Externos: proxy backend + Bearer `NOVEDADES_PROF_SYNC_TOKEN` (sync / bonos).

## Affected Areas

- `backend` proxy GET + config URL
- `frontend` `NovedadesCargaPage.jsx` + flujo editar fecha en `CargasListGrid.jsx`

## Recommendation

Proxy backend; check solo al submit/confirmar fecha; bloqueo UI fail-closed; sin revalidación en create API (Q1=A).

**v2:** si `false` en alta → modal force (motivo Vacaciones/Enfermedad + obs) Cancelar/Cargar; persistir en ambas entidades; editar fecha y error API sin force.

## Ready for Proposal

Yes — survey v1 + v2 cerradas (`decisions.md` Q1–Q15).
