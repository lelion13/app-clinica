# Implementation notes — capital-humano-grilla-actualizar

## Survey → código

| Q | Decisión | Código |
|---|----------|--------|
| Q1–Q3 | Actualizar = import bonos; default open; datos persistidos al entrar | `NovedadesXlsPage` bootstrap + `actualizar` |
| Q2 | Sin Importar bonos; Solo bonos queda | toolbar |
| Q5–Q6 | Grilla totales fijos + ajustes | columnas fijas; sin `bonoColumns` en table |
| Q7 | Detalle unificado + Agregar importe en grilla | modal Detalle 3 secciones; modal ajuste solo alta |
| Q8–Q10 | Closed disables Actualizar; elegibilidad sin cambio; Excel out | disabled + help text |

## Learnings

### F1 — Bootstrap de período open
Setear `periodoId` y `bootstrapped` antes del `loadGrid` vía `useEffect([periodoId, bootstrapped])` evita doble fetch y race al montar.

### F2 — Desglose producción sin columnas en grilla
La API sigue enviando `columns` / `bonos` / `bonos_subtotales`; la UI los usa en Detalle y solo muestra `monto_bonos` en grilla.

## Smoke (ops)

- [x] Usuario confirmó que el cambio anduvo en entorno real (2026-08-20)
