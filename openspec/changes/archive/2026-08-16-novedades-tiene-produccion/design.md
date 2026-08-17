# Design: novedades-tiene-produccion

## Decisions

See `decisions.md` Q1–Q15 (v1 + v2).

## External API / App proxy (v1)

```
GET {NOVEDADES_BONOS_TIENE_PRODUCCION_URL}?fecha=YYYY-MM-DD&codprof={CODPROF}
Authorization: Bearer {NOVEDADES_PROF_SYNC_TOKEN}
→ true | false

GET /novedades/bonos/tiene-produccion?fecha=&codprof=
→ { "tiene_produccion": boolean }
```

## Data model (v2)

On `novedades_asignacion_modulo` and `novedades_novedad`:

| Column | Type | Notes |
|--------|------|--------|
| `motivo_sin_produccion` | VARCHAR(40) NULL | `vacaciones` \| `enfermedad` |
| `observacion_sin_produccion` | VARCHAR(500) NULL | required in UI when forcing |

Alembic new revision (after current head). Both NULL when hay producción / carga normal.

## Create API (v2)

Optional fields on create módulo/novedad:

```json
{
  "motivo_sin_produccion": "vacaciones",
  "observacion_sin_produccion": "texto…"
}
```

- If either present: both MUST be valid (motivo ∈ enum, obs strip non-empty, max 500) → 422 otherwise.
- If both absent: create as today.
- Backend MUST NOT call `tiene-produccion` on create.

## UI flow (v2 alta)

1. Submit form → proxy check.
2. `true` → POST sin motivo/obs.
3. `false` → open **force modal** (not plain OK-only):
   - Text Q7
   - Select motivo (default `""`; options Vacaciones / Enfermedad)
   - Textarea observación (required)
   - **Cancelar** → close; no POST; clear carga fields (profesional, módulo, novedad, fecha)
   - **Cargar** → if missing motivo/obs show inline/modal error; else POST with fields on every entity created in that submit
4. Proxy/network error → error modal only (no force).

## UI flow editar fecha (unchanged v1)

`false` or error → block; no force modal.

## Files (v2)

| File | Action |
|------|--------|
| Alembic | Create |
| models + schemas + cargas service responses | Modify |
| `NovedadesCargaPage.jsx` (+ modal component) | Modify |
| `CargasListGrid.jsx` | Show columns or tooltip for motivo/obs |
| tests | Modify/Create |
| runbook | Modify |
