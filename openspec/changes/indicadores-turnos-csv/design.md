# Design: indicadores-turnos-csv

## API

### `POST /distribucion/ocupacion/indicadores/turnos/import`
Multipart `file`. JWT admin|operador.

1. Parse CSV (headers conocidos).
2. Período = min/max `Fecha Turno` parseable.
3. Index `nombre_agenda` normalizados del sync → set id_agenda.
4. Si algún `Nombre` no matchea → **422** `{ unmatched: [{ row, nombre }], matched, total }`.
5. Insert import header + rows (estado, fechas, nombre_norm, id_agenda preferido = min id si varios).

### `GET /distribucion/ocupacion/indicadores/turnos/stats`
Mismos query params de período/filtros que indicadores (`period`, `date`/`month`, location, room, especialidad, medico).

Response:
```json
{
  "turnos": 0,
  "ausentes": 0,
  "ausentismo_percent": null,
  "avg_presente_atendido_minutes": null,
  "avg_espera_dias": null,
  "imports": [{ "id", "filename", "period_start", "period_end", "rows" }]
}
```

## Metrics

- Universo turnos: estado in {AT, AU}, Fecha Turno in UI period, nombre_norm in agendas que pasan filtros sistema.
- Ausentes: AU en ese universo.
- % = ausentes/turnos*100.
- Avg presente→atendido: AT with both dates; mean minutes.
- Avg espera: AT with reserva+turno; mean days (fecha_turno.date - fecha_reserva.date).

## Normalize

`unicodedata NFD` strip combining + casefold + collapse spaces.

## Files

- migration `0030_turnos_csv`
- models, service `turnos_csv.py`, schemas, router
- `IndicadoresOcupacionPage.jsx`
