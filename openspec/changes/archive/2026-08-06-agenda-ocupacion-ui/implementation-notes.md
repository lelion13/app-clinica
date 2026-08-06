# Implementation notes — agenda-ocupacion-ui

Registro del change + aprendizajes de la ola Distribución/Agenda (2026-08). Incluye trabajo **fuera de este SDD** que quedó acoplado al mismo hilo.

## Estado del change

- Implementado en código (frontend principal + tests backend).
- Survey Q1–Q4 + ajuste post-deploy de filtros (ver `decisions.md`).
- **Archivado** 2026-08-06 → `openspec/changes/archive/2026-08-06-agenda-ocupacion-ui/`.
- Spec estable: `openspec/specs/distribucion/spec.md`.
- Smoke VPS post-deploy frontend: a cargo del operador.

## Qué entregó este change (`agenda-ocupacion-ui`)

1. **Alineación HORA ↔ filas** — eje de horas con marcas `position:absolute` + `box-sizing:border-box` (mismo sistema que columnas de consultorio). Causa del drift: `borderBottom` en labels con altura fija sumaba px.
2. **Layout viewport** — página full-bleed (`100vw` / `calc(50% - 50vw)`), altura `calc(100dvh - ~112px)`, grilla `flex:1; minHeight:0; overflow:auto`, cabecera HORA/consultorios `sticky`, columnas `minmax(160px, 1fr)`.
3. **Filtros** — `filter-options` + query a `agenda/events`. **UI final:** una sola fila de selects (como Ubicación): tipo / especialidad / médico / ubicación / día + nav. Vacío = sin filtro. (Survey Q3=A multi → revertido por usabilidad; ver decisiones.)
4. **Sin consultorio** — mismos filtros backend que el resto (ya aplicado en `list_agenda_events`).
5. **Modal detalle** — overlay + centrado; cierra Esc / clic overlay / Cerrar.
6. **Tests** — `test_tipo_filter_reduces_unassigned`, `test_medico_filter_reduces_unassigned`, etc.
7. **Runbook** — nota UI actualizada.

### Archivos clave (este change)

| Path | Rol |
|------|-----|
| `frontend/src/pages/AgendaOcupacionPage.jsx` | UI grilla + filtros + modal |
| `backend/tests/test_agenda_ocupacion.py` | Filtros unassigned |
| `docs/runbook.md` | Ops / UI |

---

## Fuera de este SDD (mismo hilo / PR ocupación)

Trabajo implementado **sin change SDD propio** o como follow-up de changes anteriores. Documentado aquí para no perder contexto; parte debería vivir en changes hermanos o un change retroactivo `locations-tipo`.

### A — `locations.tipo` + unique `(id_dominio, tipo)` (rev `0016`)

**Por qué:** un mismo `id_dominio` (ej. 1651) tiene muchos `tipo` en ocupación (`SEDE TORRE`, `SEDE CAÑUELAS`, …). Unique solo por `id_dominio` era incorrecto.

**Qué se hizo:**

- Migración `0016_locations_tipo`: columna `tipo` NOT NULL; placeholders `PENDIENTE-{id}`; drop `uq_locations_id_dominio_active`; create `uq_locations_id_dominio_tipo_active` (parcial `deleted_at IS NULL`).
- Model / Pydantic create+update: `tipo` obligatorio (strip).
- Service: unique por par dominio+tipo.
- UI `LocationsPage`: campo tipo en alta/edición/listado.
- Agenda: filtro por `location_id` aplica **id_dominio + tipo**; labels `(dominio, tipo_norm) → name`.

**Ops:** `alembic upgrade head` → editar ubicaciones con `PENDIENTE-*` al tipo real del sync.

**Artefacto hermano:** `openspec/changes/locations-tipo/` (documentación retroactiva).

### B — Split `nombre_agenda` con `-` compacto

**Aprendizaje:** muchas agendas vienen como `CMG-ECOGRAFIA-DR. …` **sin** `" - "` (espacio-guión-espacio). El split solo por `" - "` dejaba todo en `tipo`.

**Fix:** `horarios_activos._split_nombre_agenda` — fallback split por `-` si no hay `" - "`.

**Ops:** tras deploy backend, **Actualizar** en Ocupación (wipe+reload) para refrescar columnas derivadas.

**Impacto SDD:** delta de `distribucion-ocupacion` (Q7) asumía solo `" - "`; ver nota en `locations-tipo` / exploration actualizada abajo.

### C — Persistencia ocupación (recordatorio, change `distribucion-ocupacion`)

- `id_dato` del API **no es único** → PK serial + 1 fila DB por fila JSON.
- GET list filtra `fecha_hasta >= hoy`; sync = wipe+reload.
- Env `DISTRIBUCION_HORARIOS_*` no debe borrarse al tocar otros settings (`novedades-tiene-produccion` ya lo rompió una vez).

### D — Mapeo agenda↔consultorio (change `mapeo-agenda-consultorio`)

- Tabla `0015_room_id_agenda`; ABM en Consultorios; typeahead lookup.
- Agenda ocupación: columnas = rooms de ubicación (+ Sin consultorio).

### E — Deploy GHCR (ops, no código app)

**Síntoma (PR #5 / Backend GHCR #41):**  
`failed to build: failed to solve: failed to fetch oauth token: denied: denied`

**Hechos:** Frontend GHCR #46 **OK** en el mismo commit; Backend falló. Workflow ya tiene `packages: write` + `GITHUB_TOKEN`.

**Causa probable:** ACL del package `app-clinica-backend` en GHCR / fallo puntual de auth (no bug de Dockerfile app).

**Checklist:** Package settings → Manage Actions access (Write para el repo); Settings → Actions → Workflow permissions Read and write; Re-run Backend GHCR. Sin imagen nueva, VPS queda con backend viejo aunque el front haya subido.

---

## Aprendizajes (trampas)

### L1 — Box model en grillas por hora

No mezclar filas con `height + borderBottom` (content-box) y líneas absolutas a múltiplos exactos de `PX_PER_HOUR`. Unificar: absolute + `border-box` en ambos ejes.

### L2 — Filtros multi vs grilla útil

Listas checkbox altas roban viewport. Para agenda tipo planilla, **prioridad = grilla**. Selects de un valor en una fila > multi-select “completo”.

### L3 — Ubicación ≠ solo id_dominio

Filtrar agenda por ubicación debe usar el **par** dominio+tipo alineado al ABM y al sync.

### L4 — Derivados del sync no se “auto-arreglan”

Cambios al parser de `nombre_agenda` requieren **re-sync** (Actualizar), no solo redeploy.

### L5 — GHCR: front y back son packages independientes

Un workflow puede pasar y el otro fallar por ACL/oauth del package concreto. Verificar ambos runs antes del `compose pull` en VPS.

### L6 — Full-bleed vs `AppLayout` maxWidth

El panel usa `maxWidth: 1180`. Agenda ocupación sale con `100vw` + margen negativo para usar el monitor; no cambiar el layout global.

---

## Criterios de cierre / archive

- [ ] Frontend con filtros en una fila desplegado en VPS
- [ ] Backend con `0016` + split `-` + agenda filtro dominio+tipo en VPS (si aún no)
- [ ] Ubicaciones sin `PENDIENTE-*` (o aceptadas a propósito)
- [ ] Smoke: alineación horas, filtros, modal Esc/overlay, Sin consultorio filtra
- [ ] Archive change + fusionar delta estable a `openspec/specs/distribucion` si aplica
