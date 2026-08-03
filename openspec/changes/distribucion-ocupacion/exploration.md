# Exploration: Ocupación (horarios activos) en Distribución de consultorios

**Change:** `distribucion-ocupacion`  
**Status:** SURVEY CLOSED → proposal written  
**Created:** 2026-08-03  
**Scope:** Solo módulo **Distribución de consultorios** (no Novedades).

## Intent

Agregar un ítem de menú **Ocupación** bajo Distribución de consultorios que muestre una grilla alimentada por la API externa:

`GET https://api.cpmgsa.com.ar:8001/is/horarios-activos`  
Auth: Bearer con el mismo token que `NOVEDADES_PROF_SYNC_TOKEN` (`.env.prod`).

Columnas v1 (mínimo):

| Campo API | UI |
|-----------|-----|
| `id_dominio` | id_dominio |
| `especialidad` | especialidad |
| `fecha_desde` | fecha_desde |
| `hora_desde` | hora_desde |
| `fecha_hasta` | fecha_hasta |
| `hora_hasta` | hora_hasta |
| `duracion_turno` | duracion_turno |

Fuera de este change (explícito del pedido): relacionar con Establecimiento / Consultorios / otras solapas — se hará después.

## Current State

### Navegación Distribución

- Menú: `DistributionNavMenu` + `DISTRIBUTION_ITEMS` en `frontend/src/config/navigation.js`.
- Ítems actuales: Ocupación semanal, Agenda, Ubicaciones, Profesionales, Consultorios, Horarios consultorio, Estadística.
- Roles: `admin` y `operador` en todas las hijas de distribución.
- Home (`HomePage`) lista los mismos `DISTRIBUTION_ITEMS` como accesos rápidos.
- Ya existe **Ocupación semanal** (`/ocupacion-semanal` → `WeeklyOccupancyPage`) — cálculo local de ocupación de consultorios; **no** consume `horarios-activos`.

### Integraciones HTTP externas (patrón a reutilizar)

- Novedades sync profesionales: `backend/app/services/novedades/prof_sync.py` — `httpx` + Bearer + URL/TOKEN/TIMEOUT desde env; el frontend **nunca** ve el token.
- Bonos: reutiliza el mismo `NOVEDADES_PROF_SYNC_TOKEN` con otra URL.
- Config: `backend/app/core/config.py` (`novedades_prof_sync_*`).

### Auth

- Rutas API protegidas con JWT (cookie HttpOnly); roles admin/operador para distribución.

## Affected Areas (previsto)

- `frontend/src/config/navigation.js` — nuevo ítem Ocupación (+ path)
- `frontend/src/main.jsx` — ruta
- `frontend/src/pages/` — nueva página grilla (nombre TBD)
- `backend/app/api/routers/` — endpoint proxy JWT-protegido
- `backend/app/services/` — cliente HTTP a `horarios-activos`
- `backend/app/schemas/` — respuesta Pydantic (subset columnas)
- `backend/app/core/config.py` + `.env.example` / `.env.prod.example` — URL (y posiblemente timeout) del endpoint
- Tests backend del proxy / errores 502/422

## Approaches

1. **Proxy BFF (recomendado)** — Backend FastAPI expone p.ej. `GET /api/v1/distribucion/ocupacion/horarios-activos` (JWT). Internamente llama a la API externa con Bearer del env. Frontend solo consume la API propia.
   - Pros: token no llega al browser; mismo patrón que Novedades; errores controlados (502/422).
   - Cons: un hop más; hay que definir env URL/timeout.
   - Effort: Medium

2. **Sync a tabla local** — Job o botón que persiste filas en PostgreSQL y la UI lee de DB.
   - Pros: filtro/join futuro con consultorios; offline-ish.
   - Cons: fuera del “por ahora grilla”; migraciones; staleness; más alcance.
   - Effort: High

3. **Fetch directo desde el frontend** — React llama a `api.cpmgsa.com.ar` con token.
   - Pros: menos código backend.
   - Cons: **rechazado por seguridad** (token en cliente / CORS / exposición).
   - Effort: Low (pero no viable)

## Recommendation

**Approach 1 (proxy BFF)** reutilizando el patrón de `prof_sync` / bonos: nueva URL de env (p.ej. `DISTRIBUCION_HORARIOS_ACTIVOS_URL`), reutilizar `NOVEDADES_PROF_SYNC_TOKEN` como pidió el usuario, timeout propio o compartido. UI: página + grilla read-only con las 7 columnas.

Pendiente de survey: relación con el ítem existente **Ocupación semanal**, roles, carga live vs cache, filtros v1.

## Risks

- Confusión de nombres con **Ocupación semanal** (ya en menú).
- Volumen del JSON externo (grilla sin paginación puede ser pesada).
- Token compartido con Novedades: rotación afecta ambos; no loguear token.
- API externa caída → UX debe degradar con error genérico (502), sin filtrar el token.
- Relación futura con consultorios/establecimiento no definida aún (`id_dominio`, `consultorio`, etc.).

## Open questions (survey)

Ver `decisions.md`. Una pregunta a la vez.

## Ready for Proposal

**Yes** — survey Q1–Q6 = A. `proposal.md` escrito. Siguiente: specs → design → tasks.
