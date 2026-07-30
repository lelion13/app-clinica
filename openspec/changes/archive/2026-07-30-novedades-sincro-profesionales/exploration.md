# Exploration: Sync profesionales (API externa) para Novedades

**Change:** `novedades-sincro-profesionales`  
**Status:** Archived 2026-07-30  
**Created:** 2026-07-29 · Survey cerrada → proposal/spec/design/tasks → apply → archive

## Intent

Ver `proposal.md` / `implementation-notes.md`. Catálogo Novedades HTTP aparte de Distribución.

## Current State (al archivar)

- Tabla `novedades_profesional` + sync HTTP + purge implementados.
- Novedades FKs → `novedades_profesional.id`.
- Distribución `professionals` / MySQL sync sin cambios.

## Decisions

Ver `decisions.md` (Q1–Q13). Resumen en `implementation-notes.md`.

## Ready for Proposal

N/A — change archivado. Spec estable: `openspec/specs/novedades/spec.md`.

## Intent

Ver `proposal.md`. Resumen: catálogo Novedades aparte (HTTP), sync manual, inactivar ausentes, limpiar transaccional con hard-delete controlado.

## Current State (código)

- Tabla `professionals` + sync MySQL (`POST /professionals/sync`) para Distribución.
- Novedades hoy FK a `professionals.id`.
- Sin cliente HTTP a `api.cpmgsa.com.ar`.

## Decisions (survey Q1–Q13)

Ver `decisions.md` (fuente de verdad). Resumen:

| ID | Decisión |
|----|----------|
| Q1=A | Dos catálogos |
| Q2 | Match `CODPROF` string + leading zeros |
| Q3=D / Q4=A | Limpiar cargas + vínculos; conservar param |
| Q5=C | Sync: param admin/rrhh; Mis prof. + jefe |
| Q6=A | Solo sync (sin ABM) |
| Q7=C | Vínculo a inactivo visible; limpieza manual; sin cargas |
| Q8=B | `CODPROV` guardado, sin UI |
| Q9=B / Q11=B / Q12=A | Botón limpiar en Param; hard-delete + confirm |
| Q10=A | Reactivar si vuelve en sync |
| Q13=A | Resumen sync en AlertModal |

## Approaches

1. **Catálogo Novedades separado (elegido, Q1=A)** — tabla nueva + rewire FKs; Distribución intacta.
2. ~~Misma tabla + source~~ — descartado.
3. ~~Unificar sync HTTP para todos~~ — descartado.

## Recommendation

Approach 1 según survey. Detalle técnico en `design.md` (siguiente fase).

## Risks

- Hard-delete irreversible sin backup.
- Token no debe vivir en repo; rotar si expuesto.
- No inactivar locales si falla el GET externo.

## Ready for Proposal

**Yes** — `proposal.md` escrito. Siguiente: specs → design → tasks.
