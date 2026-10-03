# Design: Indicadores ocupación

## Technical Approach

Endpoint + servicio nuevos bajo distribución, separados de `stats_service` (bookings). Reutilizar parsing dia/hora/vigencia de `agenda_ocupacion` (extraer helpers compartidos o importar funciones privadas con cuidado). Front: página nueva con recharts `Pie` como `EstadisticasPage`.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| No reusar `/stats` | Q6=A; evita mezclar bookings vs sync |
| Cálculo server-side por `date` | Una fuente de verdad; filtros en query |
| Numerador = duración bloque completa | Q9=C |
| `free_hours_display = max(0, enabled - occupied)` para porción torta | Evita negativos; el % real va en KPI textual (Q10=A) |
| Especialidad/médico solo en query de sync | Q8=A1 |
| Rooms sin horario → array aparte | Q5=C |
| Soft-delete rooms excluidos | Consistente con resto ABM |

## Calculation (pseudocode)

```
rooms = active rooms filtered by location_id?, room_id?
for room in rooms:
  hours = operating hours that weekday
  if no hours: rooms_without_hours.append(room); continue
  enabled += hours
  if room has no mapped agendas: continue  # occupied += 0
  for each sync block that day for mapped id_agendas:
    if especialidad/medico filters miss: skip
    occupied += (hora_hasta - hora_desde)  # full block, no clip
percent = occupied/enabled*100 if enabled>0 else null
pie = [{ocupado: occupied}, {libre: max(0, enabled-occupied)}]
```

Weekday: `weekday_js_from_date` + match sync `dia` como agenda ocupación.

## API sketch

`GET /api/v1/distribucion/ocupacion/indicadores?date=YYYY-MM-DD&location_id=&room_id=&especialidad=&medico=`

Response (ilustrativo):

```json
{
  "date": "2026-08-06",
  "occupied_hours": 12.5,
  "enabled_hours": 40,
  "free_hours": 27.5,
  "occupancy_percent": 31.25,
  "rooms_included": 10,
  "rooms_without_hours": [{"id": 3, "code": "401"}],
  "rooms_without_agenda": 2
}
```

Opciones de filtros: reutilizar `/locations`, `/consulting-rooms`, y `agenda/filter-options` (especialidad/médico) o embebidas.

## File-Level Changes

| File | Change |
|------|--------|
| `backend/app/services/distribucion/indicadores_ocupacion.py` | New |
| `backend/app/schemas/distribucion.py` | Response models |
| `backend/app/api/routers/distribucion.py` | Route |
| `backend/tests/test_indicadores_ocupacion.py` | New |
| `frontend/src/pages/IndicadoresOcupacionPage.jsx` | New |
| `frontend/src/config/navigation.js` | Item |
| `frontend/src/main.jsx` | Route |
| `docs/runbook.md` | Note |

## Alternatives Considered

| Alt | Why rejected |
|-----|----------------|
| Extender Estadística | User Q6=A menú aparte |
| Capar % 100 | Q10=A |
| Clip sync a operating hours | Q9=C |

## Testing Strategy

- Unit: sin agenda → num 0; sin horario → lista; bloque 4h vs enabled 3h → % >100; filtro médico no cambia enabled.
- Manual: abrir página, cambiar día/filtros, torta + aviso sin horario.

## Migration / Rollout

Sin migración. Deploy backend+frontend. Depende de sync + mapeos + horarios box cargados.
