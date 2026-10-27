# Design: novedades-param-recalculo

## Data note
Module assignments already snapshot `valor`. Novedades historically computed importe live from `servicio.valor_hora`. Implemented persisted `novedades_novedad.valor` (rev `0035`: backfill + NOT NULL; set on create/update; CH/grid/export read persisted valor) so recalc hours is meaningful.

## Recálculo APIs (`admin`/`rrhh`)
- `POST /novedades/recalculo/preview` `{periodo_id, modo: horas|modulos|ambos}`
- `POST /novedades/recalculo/apply` same body; rejects if zero changes

### Logic
- Modulos: new = `modulo_valor_para_profesional(...)`; change if ≠ persisted
- Horas: new = `novedad_valor_calculado(tipo, horas, servicio.valor_hora)`; change if ≠ persisted `valor`
- Preview aggregates by modulo_id + hours block totals
- Soft-delete excluded; open or closed period OK

### UI
Tab **Recálculo** after Feriados: período, modo, Vista previa, resumen, Confirmar.

## Valores Extras (Índices, `admin`)

### APIs
- `GET /novedades/indices/valores-extras?periodo_id&filtro&q`
  - `filtro`: `ambos` | `modulos` | `novedades` | `novedad_extra`
  - `novedad_extra`: filas con alguna observación no vacía (hoy `observacion_sin_produccion`)
  - Agrupa por profesional con totales + detalle
- `POST /novedades/indices/valores-extras/pdf` body `{periodo_id, filtro, q?, professional_ids[]}`
  - Un PDF A4; page break por profesional; chrome = app-recepcion (`pdf-header-band.png` + banda título + footer)

### UI
Botón **Valores Extras** (disabled sin período) → modal: filtros, búsqueda, grilla expandible, checkboxes (fila + todos), **Exportar** | **Cerrar**.

### Deps
`reportlab>=4.2.0`; asset `backend/app/assets/pdf-header-band.png`.
