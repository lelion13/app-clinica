# Exploration: Capital Humano + LEGAJO en catálogo Novedades

**Change:** `novedades-capital-humano-legajo`  
**Status:** Survey cerrada → proposal listo  
**Created:** 2026-07-30

## Intent

Ver `proposal.md`. LEGAJO en sync + pantalla Capital Humano (grilla agregada + ajustes + 2 XLS).

## Current State (código)

- `NovedadesProfesional` sin `legajo`; sync sin `LEGAJO`.
- `/novedades/xls` = grilla detalle por carga + un download XLS.

## Decisions (Q1–Q11)

Ver `decisions.md`. Resumen:

| ID | Decisión |
|----|----------|
| Q1=A | Total = cargas en período (± servicio) |
| Q2=A | Ajustes persistidos; total = cargas ± ajustes |
| Q3=A | Ajustes admin/rrhh |
| Q4=A | Solo alta de ajustes |
| Q5=A | LEGAJO string + trim + leading zeros |
| Q6=D | 2 XLS (agregada + detalle) |
| Q7=A | LEGAJO null OK |
| Q8=C | Columna ajustes → historial + alta |
| Q9=B | Ajustes OK con período cerrado |
| Q10=A | Importe con signo + comentario |
| Q11=A | Filas solo con carga o ajuste en alcance |

## Ready for Proposal

**Yes** — `proposal.md` escrito. Siguiente: specs → design → tasks.
