# Proposal: Capital Humano — visibilidad motivos sin producción

## Intent

RRHH necesita detectar en Capital Humano las cargas hechas bajo el flujo “sin producción” / novedad extra (`motivo_sin_produccion` Vacaciones o Enfermedad), sin ir a Carga. Hoy ese dato existe en DB y en Carga, pero no en la grilla CH, Detalle ni Excel detalle.

## Scope

### In Scope
- Select Motivo en CH: `Todos` · `Vacaciones` · `Enfermedad`
- Resaltar con **un color** las filas de profesionales que tengan ≥1 carga con motivo (según select); no ocultar filas
- Botón **Con novedad** → modal con lista plana de cargas que matchean el select
- Detalle Cargas: columnas **Motivo** y **Observación**
- `GET /novedades/grilla` + `export.xlsx`: incluir motivo/observación en filas y columnas XLS
- Payload capital-humano: datos suficientes para saber qué profesionales resaltar

### Out of Scope
- Nuevos valores de motivo (solo vacaciones/enfermedad)
- Filtrar/ocultar profesionales de la grilla por motivo
- Recalcular totales de fila según motivo
- Cambiar liquidación / exports agregados / descarga parcial
- Colores distintos por tipo de motivo

## Approach

Exponer `motivo_sin_produccion` y `observacion_sin_produccion` en `GridRowResponse` y en el XLS detalle. En capital-humano, agregar flags (o set de motivos) por profesional derivados de las cargas del período. UI: select + highlight + modal alimentado por `/grilla` (filtro client-side o query) según el select.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/.../schemas/novedades.py` | Modified | Motivo/obs en GridRow; flags en fila CH |
| `backend/.../export_xls.py` | Modified | Mapear campos + columnas XLS |
| `backend/.../capital_humano.py` | Modified | Flags por profesional |
| `frontend/.../NovedadesXlsPage.jsx` | Modified | Select, highlight, modal, Detalle |
| `docs/runbook.md` | Modified | Nota breve |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Filas CH sin cargas en `/grilla` (solo bonos) no tienen motivo | Low | Solo resaltar si hay cargas con motivo |
| Modal vacío con select Vacaciones | Low | Mensaje “Sin cargas” |

## Rollback Plan

Revert FE toolbar/Detalle/modal y campos nuevos en schema/export/CH; sin migración DB (columnas ya existen).

## Dependencies

- Datos ya persistidos por cambios `novedades-tiene-produccion` / `novedades-carga-novedad-extra`

## Success Criteria

- [ ] Select + highlight funcionan (Todos / Vacaciones / Enfermedad)
- [ ] Botón **Con novedad** lista las cargas correctas
- [ ] Detalle y Excel detalle muestran Motivo y Observación
- [ ] Profesionales sin motivo no se resaltan
