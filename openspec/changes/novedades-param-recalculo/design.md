# Design: novedades-param-recalculo

## Data note
Module assignments already snapshot `valor`. Novedades historically computed importe live from `servicio.valor_hora`. Implemented persisted `novedades_novedad.valor` (rev `0035`: backfill + NOT NULL; set on create/update; CH/grid/export read persisted valor) so recalc hours is meaningful.

## APIs (`admin`/`rrhh`)
- `POST /novedades/recalculo/preview` `{periodo_id, modo: horas|modulos|ambos}`
- `POST /novedades/recalculo/apply` same body; rejects if zero changes

## Logic
- Modulos: new = `modulo_valor_para_profesional(catalog, es_especialista, servicio.especialista)`; change if ≠ persisted
- Horas: new = `novedad_valor_calculado(tipo, horas, servicio.valor_hora)`; change if ≠ persisted `valor`
- Preview aggregates by modulo_id + hours block totals
- Soft-delete excluded; open or closed period OK

## UI
Tab **Recálculo** after Feriados: período, modo, Vista previa, resumen, Confirmar.
