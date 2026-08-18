# Proposal: Control tiene-producción en Carga

## Intent

Cuando admin/jefe intenta cargar módulo/novedad o editar la fecha de realización, verificar contra producción externa (`/bonos/tiene-produccion?fecha&codprof`).

**v1:** si `false` o error API → bloquear.  
**v2:** si `false` → modal con motivo + observación obligatorios y botones Cancelar / Cargar; Cargar persiste la excepción y crea la carga. Error API sigue bloqueando sin force. Editar fecha sigue bloqueo simple (sin force).

## Scope

### In Scope (v1 — hecho)

- Proxy backend + env URL; check al Cargar y al editar fecha; roles admin/jefe.

### In Scope (v2)

- Modal cuando `tiene_produccion === false`: mensaje Q7 + combo motivo (default vacío; opciones Vacaciones / Enfermedad) + observación obligatoria.
- Botones: **Cancelar** (cierra, no carga) y **Cargar** (valida motivo+obs → POST con esos campos).
- Persistencia: columnas `motivo_sin_produccion` + `observacion_sin_produccion` (nombres a definir en design) en asignación y novedad; mismo valor en ambas si se crean juntas.
- Mostrar motivo/obs en grilla o detalle de Carga.
- Alembic + schemas create/response + UI modal dedicado (no solo AlertModal OK).

### Out of Scope

- Revalidar `tiene-produccion` en backend create (Q1/Q14=A).
- Force-load al editar fecha (Q11=B).
- Force-load cuando el API falla (Q12=A).
- ABM de motivos (lista fija).
- RRHH / Capital Humano.

## Approach (v2)

1. Migración: campos nullable en `novedades_asignacion_modulo` y `novedades_novedad`.
2. Create payloads aceptan opcionales motivo/obs; si vienen, validar enum + obs no vacía.
3. Front: al `false`, abrir modal force; Cancelar aborta; Cargar rellena payload y ejecuta POSTs.

## Risks

| Risk | Mitigation |
|------|------------|
| Bypass sin motivo vía API | Aceptado Q14=A; documentar |
| Confusión editar fecha vs alta | Copy distinto; sin force en fecha |

## Success Criteria (v2)

- `false` → modal con combo vacío + obs; Cancelar no POST.
- Cargar sin motivo o sin obs → no POST (validación UI).
- Cargar OK → crea carga(s) con motivo/obs persistidos.
- API error → modal error, sin force.
- Editar fecha + false → bloqueo simple.
