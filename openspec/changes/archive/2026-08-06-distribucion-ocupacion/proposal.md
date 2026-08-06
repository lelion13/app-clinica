# Proposal: Ocupación (horarios activos) — Distribución

## Intent

Exponer en Distribución de consultorios una vista **Ocupación** con horarios activos de la API externa `GET …/is/horarios-activos`, sin mezclar con Novedades ni con la pantalla existente **Ocupación semanal**.

## Scope

### In Scope

- Ítem menú **Ocupación** → `/ocupacion` (convive con Ocupación semanal).
- Backend proxy JWT (`admin`/`operador`): GET propio → HTTP externo con Bearer `NOVEDADES_PROF_SYNC_TOKEN`.
- Env: `DISTRIBUCION_HORARIOS_ACTIVOS_URL` (+ timeout opcional); documentar en `.env.example` / `.env.prod.example`.
- Frontend: grilla read-only auto-load + “Actualizar”.
- Columnas v1: `id_dominio`, `especialidad`, `fecha_desde`, `hora_desde`, `fecha_hasta`, `hora_hasta`, `duracion_turno`.
- Tests del proxy (config ausente, error upstream, happy path).

### Out of Scope

- Persistencia / sync a PostgreSQL.
- Relación con establecimientos, consultorios u otras solapas.
- Cambios a Ocupación semanal, Novedades, o ABM usuarios.
- Filtros avanzados, export, edición.

## Approach

Proxy BFF (mismo patrón que `novedades/prof_sync`): servicio `httpx` + schema Pydantic del subset; router bajo API de distribución; página React en `DISTRIBUTION_ITEMS`. Token nunca al cliente.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `frontend/src/config/navigation.js` | Modified | Ítem Ocupación |
| `frontend/src/main.jsx` | Modified | Ruta `/ocupacion` |
| `frontend/src/pages/` | New | Página grilla |
| `backend/app/core/config.py` | Modified | URL/timeout |
| `backend/app/api/routers/` | New/Modified | Endpoint proxy |
| `backend/app/services/` | New | Cliente HTTP |
| `backend/app/schemas/` | New | Response rows |
| `.env.example`, `.env.prod.example` | Modified | Vars públicas |
| `backend/tests/` | New | Proxy tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Token expuesto en logs/errores | Med | Mensajes genéricos; no loguear headers |
| API externa lenta/caída | Med | Timeout + 502; UI error claro |
| Volumen grande en grilla | Med | v1 lista completa; paginar/filtrar después |
| Confusión con Ocupación semanal | Low | Labels/paths distintos |

## Rollback Plan

Revertir deploy del front/back; quitar vars nuevas del env. Sin migraciones DB.

## Dependencies

- API externa `api.cpmgsa.com.ar:8001/is/horarios-activos` reachable desde el backend.
- `NOVEDADES_PROF_SYNC_TOKEN` válido en prod.

## Success Criteria

- [ ] Menú Distribución muestra Ocupación y Ocupación semanal.
- [ ] `admin`/`operador` ven grilla con las 7 columnas tras login JWT.
- [ ] Token no aparece en red del browser ni en respuestas de error.
- [ ] Sin URL/token → error controlado (422); upstream fail → 502.
- [ ] `.env*.example` actualizados (sin secretos).

## Decisions

Ver `decisions.md` (Q1–Q6 = A). Survey CLOSED.
