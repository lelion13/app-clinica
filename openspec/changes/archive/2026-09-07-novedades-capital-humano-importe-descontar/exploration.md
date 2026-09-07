# Exploration: novedades-capital-humano-importe-descontar

## Current State

- Capital Humano (`NovedadesXlsPage`): grilla 1 fila/profesional; **Agregar importe** → `POST /novedades/capital-humano/ajustes` (`NovedadesAjusteCapital`: professional + período + `servicio_id` opcional + importe + comentario ≤500).
- Ajustes permitidos con período cerrado; `importe == 0` rechazado.
- Totales: `monto_total = cargas + ajustes + producción` (producción = bonos/prácticas/internaciones valorizados).
- Precedent import Excel todo-o-nada: `modulos_import.py` + modal de errores por fila.
- **Descargar liquidación** ya existe; hoy prorratea **todos** los ajustes en partes iguales por concepto (ignora `servicio_id`).

## Affected Areas

- `backend/app/models/novedades.py` — marcar ajustes de import (lote / origen)
- `backend/app/services/novedades/` — nuevo import descuento + anular; reusar grilla/cargas por servicio
- `backend/app/api/routers/novedades.py` — endpoints import / anular / estado
- `backend/app/schemas/novedades.py` — request/response errores
- `frontend/src/pages/novedades/NovedadesXlsPage.jsx` — botón antes de liquidación + modales
- Posible: `liquidacion_export.py` — respetar `servicio_id` en ajustes (consistencia)

## Approaches

1. **Lote en `novedades_ajuste_capital`** — columna `descuento_lote_id` (UUID) o `origen=importe_descontar`; import crea N ajustes (waterfill); Anular soft-delete por lote del período.
   - Pros: reusa modelo/grilla/Detalle; Anular preciso; un solo lote activo por período.
   - Cons: migración; liquidación hoy no usa `servicio_id`.
   - Effort: Medium

2. **Tabla aparte de descuentos** — no pasa por ajustes.
   - Pros: aislamiento.
   - Cons: duplica totales/Detalle/export; contradice “imputar como Agregar importe”.
   - Effort: High

3. **Solo comentario-marker** — sin migración.
   - Pros: rápido.
   - Cons: Anular frágil; colisión con ajustes manuales.
   - Effort: Low

## Recommendation

**Approach 1.** Endpoint import multipart (período cerrado) + anular lote + flag/estado para UI. Waterfill por servicios de carga (mayor monto primero; empate indistinto); tope `cargas+producción`; solo-producción → 1 ajuste `servicio_id=NULL`. Todo-o-nada; modal con **todos** los errores. En design: alinear liquidación con `servicio_id` cuando exista.

## Decisions (survey)

Ver `decisions.md` (Q1–Q25).

## Risks

- Liquidación re-prorratea ajustes y puede deshacer el waterfill por servicio → mitigar en design/apply.
- Comentario truncado a 500 puede perder Sector/Monto al final.
- Empate de montos de carga no determinista (aceptado).

## Ready for Proposal

Yes — proposal next; luego specs/design.
