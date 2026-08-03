# Decisions: novedades-tiene-produccion

**Survey cerrada** (2026-08-03).

## Checklist

- [x] Q1 — UI only vs backend enforcement
- [x] Q2 — Roles afectados (solo jefe vs admin también)
- [x] Q3 — Fuente de `codprof` (campo API vs id interno)
- [x] Q4 — Cuándo disparar el check (debounce / on change)
- [x] Q4b — Front → API externo directo vs proxy backend (token)
- [x] Q5 — Si el API externo falla (timeout/5xx)
- [x] Q6 — Alcance: solo Carga o también otros flujos
- [x] Q7 — Texto del modal cuando `false`
- [x] Q8 — URL env (default documentado)

---

## Q1 — Enforcement

**Elegido: A** — Solo UI (modal + no permitir cargar). El backend **no** revalida `tiene-produccion` al crear.

## Q2 — Roles

**Elegido: B** — Aplica a `jefe_medico` y `admin` (quienes pueden cargar).

## Q3 — Valor `codprof`

**Elegido: A** — Usar `novedades_profesional.codprof` del profesional seleccionado (no el id interno ni legajo).

## Q4 — Momento del check

**Elegido: B** — Solo al intentar pulsar **Cargar** (antes de enviar el alta). Si `false` → modal y no envía.

## Q4b — Proxy

**Elegido: A** — Front → endpoint propio; backend llama al externo con Bearer (mismo token sync/bonos) y responde true/false. Token no en el browser.

## Q5 — Fallo del API

**Elegido: A** — Bloquear la carga: modal de error y no enviar (fail-closed).

## Q6 — Alcance

**Elegido: C** — Página Carga: al **alta** y también al **editar fecha** de una carga existente (mismo check fecha + codprof).

## Q7 — Copy modal `false`

**Elegido: A** — “El profesional no tiene producción en esa fecha. No se puede cargar módulo ni novedad para ese día.”

## Q8 — Config URL

**Elegido: A** — Env `NOVEDADES_BONOS_TIENE_PRODUCCION_URL` con default `https://api.cpmgsa.com.ar:8001/bonos/tiene-produccion`; token = `NOVEDADES_PROF_SYNC_TOKEN`.
