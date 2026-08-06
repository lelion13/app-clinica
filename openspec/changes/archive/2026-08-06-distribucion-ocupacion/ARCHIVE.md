# Cierre — distribucion-ocupacion

**Archivado:** 2026-08-06 → `openspec/changes/archive/2026-08-06-distribucion-ocupacion/`

## Alcance final (implementado)

- Menú `/ocupacion` + grilla + filtros + Indicadores + Actualizar=sync
- Tabla `ocupacion_horario_activo` con **PK serial** (rev `0013`; `id_dato` **no** es único)
- Sync wipe+reload; GET `fecha_hasta >= hoy`
- Env `DISTRIBUCION_HORARIOS_ACTIVOS_*` + Bearer `NOVEDADES_PROF_SYNC_TOKEN`
- Split `nombre_agenda`: `" - "` o fallback `-`
- `locations.id_dominio` (0014) — el `tipo` (0016) vive en archive `locations-tipo`

## Superseded / no reabrir

| Tema | Dónde está la verdad |
|------|----------------------|
| Texto antiguo “PK id_dato” en drafts tempranos | Spec estable + este ARCHIVE |
| UI Agenda ocupación | `agenda-ocupacion-ui` + spec estable § UI |
| locations.tipo | `locations-tipo` |

## Spec estable

`openspec/specs/distribucion/spec.md` — secciones Sync y Ocupación + Split.
