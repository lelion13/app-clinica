# Proposal: indicadores-turnos-csv

## Intent

Probar en Indicadores ocupación la importación de un CSV de turnos reales (AT/AU/…) matcheado por nombre de agenda, con KPIs filtrables debajo de la torta.

## Scope

### In Scope
- Botón **Importar datos de turnos** en `/indicadores-ocupacion`.
- Upload CSV (formato ejemplo `092026_cmg.csv`); persistir en DB con filename + período (min–max Fecha Turno).
- Match exacto normalizado `Nombre` ↔ `nombre_agenda` del sync; si alguna fila no matchea → rechazar import + modal con detalle.
- Varios imports pueden coexistir (mismo período OK).
- Panel bajo la torta: cantidad turnos (AT+AU), ausentes (AU), % ausentismo, avg min presente→atendido (AT), avg días espera reserva→turno (AT).
- Recalcular según período Día|Mes y filtros ubicación/consultorio/especialidad/médico (vía agenda del sistema).

### Out of Scope
- Match fuzzy / tabla de equivalencias.
- Looker Studio / API externa.
- Cambiar fórmula de la torta sync÷box.
- Edición manual de filas importadas.

## Approach

1. Tablas `turnos_csv_import` + `turnos_csv_row`.
2. `POST .../ocupacion/indicadores/turnos/import` (multipart); `GET .../turnos/stats` con mismos filtros que indicadores.
3. UI: botón + file input; modal unmatched; KPI strip bajo torta/tops.

## Success Criteria

- [ ] Import OK solo si todos los Nombre matchean sync.
- [ ] KPIs respetan período UI + filtros.
- [ ] Re-import suma otro lote.
- [ ] Tests parse/match/stats.
