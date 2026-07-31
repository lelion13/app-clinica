# Design: capital-humano-bonos-resumen

## Decisions

See `decisions.md` Q1–Q10.

## Data model

Suggested (implementation MAY adjust names):

**`novedades_bono_opcion`** (dimensión estable de columnas)
- `id`, `centro`, `servicio`, `semana`, `horario`
- UNIQUE(`centro`,`servicio`,`semana`,`horario`)
- `label` opcional o derivado para header UI

**`novedades_bono_cantidad`** (snapshot por período)
- `id`, `periodo_id` FK, `professional_id` FK → `novedades_profesional`
- `opcion_id` FK, `cantidad` Integer/Numeric
- UNIQUE(`periodo_id`,`professional_id`,`opcion_id`)
- audit fields

Import con período **open**: en transacción, borrar todas las filas de `novedades_bono_cantidad` del `periodo_id` y reinsertar desde el API (replace). Período **closed**: rechazar.

## External API

```
GET {NOVEDADES_BONOS_RESUMEN_URL}?fecha_desde=YYYY-MM-DD&fecha_hasta=YYYY-MM-DD
Authorization: Bearer {NOVEDADES_PROF_SYNC_TOKEN}
```

Item:
```json
{
  "centro": "CMG",
  "servicio": "CAP",
  "semana": "LUNES_VIERNES",
  "horario": "DIA",
  "profesional": "111",
  "cantidad": 160
}
```

- `profesional` → match `novedades_profesional.codprof` (string trim).
- Opción key = `(centro, servicio, semana, horario)`; header UI ej. `CMG · CAP · LUNES_VIERNES · DIA`.
- Duplicados misma clave+profesional: **sumar** cantidad.
- CODPROF desconocido: ignorar (conteo en resumen).

## API (app)

| Method | Path | Notes |
|--------|------|-------|
| POST | `/novedades/capital-humano/bonos/import` | body `{ periodo_id }`; admin/rrhh; summary response |
| GET | `/novedades/capital-humano` | incluir `bonos: { [opcionKey]: cantidad }` + lista `bono_columnas` (o endpoint metadatos) |
| GET | `/novedades/capital-humano/bonos/solo` | `periodo_id` → profesionales catálogo con bonos y sin cargas/ajustes |
| GET | `/novedades/export-capital-bonos.xlsx` | agregado + columnas bonos |

## UI

- Select período **obligatorio** para Importar bonos (si “Todos los períodos” → error/modal).
- Botón **Importar bonos** disabled si período closed o sin selección.
- Columnas dinámicas a la derecha (solo opciones presentes en el snapshot del período filtrado).
- Botón para abrir modal **Solo bonos**.
- Tercer botón **XLS con bonos**.
- AlertModal resumen / errores.

## Config

- `NOVEDADES_BONOS_RESUMEN_URL` (default documentado)
- Reutilizar `NOVEDADES_PROF_SYNC_TOKEN` (+ timeout existente o `NOVEDADES_BONOS_RESUMEN_TIMEOUT`)

## Files

| File | Action |
|------|--------|
| Alembic `0010_...` | Create |
| models/schemas/services | Create/Modify |
| router + config | Modify |
| NovedadesXlsPage.jsx | Modify |
| tests + runbook | Modify |
