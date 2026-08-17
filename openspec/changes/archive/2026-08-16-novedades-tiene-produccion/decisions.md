# Decisions: novedades-tiene-produccion

**Survey v1 cerrada** (2026-08-03).  
**Survey v2 (modal force-load) cerrada** (2026-08-13).

## Checklist v1

- [x] Q1 — UI only vs backend enforcement
- [x] Q2 — Roles afectados (solo jefe vs admin también)
- [x] Q3 — Fuente de `codprof` (campo API vs id interno)
- [x] Q4 — Cuándo disparar el check (debounce / on change)
- [x] Q4b — Front → API externo directo vs proxy backend (token)
- [x] Q5 — Si el API externo falla (timeout/5xx)
- [x] Q6 — Alcance: solo Carga o también otros flujos
- [x] Q7 — Texto del modal cuando `false`
- [x] Q8 — URL env (default documentado)

## Checklist v2 — modal sin producción → force load

- [x] Q9 — Opciones del selector “tipo de motivo” (lista fija vs catálogo)
- [x] Q9b — ¿Solo esos dos motivos o hay más?
- [x] Q10 — ¿Se persisten motivo + observación en la carga?
- [x] Q11 — ¿Aplica igual al editar fecha?
- [x] Q12 — Si el API de producción **falla** (no `false`): ¿mismo modal force o solo error?
- [x] Q13 — Roles que pueden forzar la carga con motivo
- [x] Q14 — Backend: ¿exige motivo/obs al crear? (vs solo UI)
- [x] Q15 — Si se cargan módulo y novedad juntos, ¿mismo motivo/obs en ambos?

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

---

# Survey v2 — force load con motivo (cerrada)

## Q9 — Selector motivo

**Elegido: A** — Lista fija en código. Default del combo: **vacío** (obligatorio elegir).

## Q9b — Opciones

**Elegido: A** — Solo: `Vacaciones`, `Enfermedad` (+ placeholder vacío por defecto).

## Q10 — Persistencia

**Elegido: A** — Persistir motivo + observación en la asignación/novedad (campos nuevos) y mostrarlos en listados/detalle según aplique.

## Q11 — Editar fecha

**Elegido: B** — Al editar fecha **no** hay force-load: sigue bloqueo simple (modal de error / sin producción, sin combo ni Cargar forzado).

## Q12 — Fallo API vs `false`

**Elegido: A** — Si el API falla: solo error técnico (bloquea). Force con motivo **solo** cuando responde `false`.

## Q13 — Roles force

**Elegido: A** — `admin` y `jefe_medico` (igual que Carga).

## Q14 — Validación backend

**Elegido: A** — Solo UI fuerza el flujo. Backend acepta motivo/obs si vienen; **no** reconsulta `tiene-produccion` ni los exige siempre.

## Q15 — Módulo + novedad juntos

**Elegido: A** — El mismo motivo + observación se guardan en **ambas** filas creadas en ese submit.
