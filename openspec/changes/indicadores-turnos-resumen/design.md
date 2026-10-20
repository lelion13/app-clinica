# Design: indicadores-turnos-resumen

## Context

Indicadores ocupación ya carga filas sync + torta. La clínica dispone de un endpoint externo de **resumen de turnos** por rango de fechas; cada fila trae `turno_horario_id` alineable al `id` del horario de ocupación. Hoy Ocupación no muestra/asegura `id` en la grilla; Indicadores no consume ese resumen.

## Goals / Non-Goals

**Goals:** id en Ocupación; proxy BE; Indicadores async + join + filtros en memoria; agregación A; fallo no bloqueante.

**Non-Goals:** charts; cache DB; cambiar import CSV ni fórmulas de ocupación; fetch por cada cambio de filtro.

## Architecture

```
[Ocupación Actualizar] → body con id → DB → GET /ocupacion (id + campos)
[Indicadores]
  period/date|month change
       → GET /api/.../ocupacion/indicadores/turnos-resumen?fecha_desde&fecha_hasta
       → BE fetch DISTRIBUCION_TURNOS_RESUMEN_URL + Bearer token
       → FE: filtrar rows donde turno_horario_id ∈ ids del set filtrado
       → agregar → bloque UI
  filtros (agenda/día/horario/estado)
       → solo re-filtrar + re-agregar en memoria (sin re-fetch)
```

## Data contracts

### Ocupación (ya en sync; asegurar en API/UI)

Cada fila activa incluye `id` (int, PK horario remoto).

### Externo (shape de referencia)

```json
{
  "fecha_desde": "YYYY-MM-DD",
  "fecha_hasta": "YYYY-MM-DD",
  "total_turnos": 0,
  "detalle": [
    {
      "turno_horario_id": 123,
      "total_turnos": 0,
      "turnos_pendientes": 0,
      "turnos_confirmados": 0,
      "turnos_cancelados": 0,
      "turnos_atendidos": 0,
      "turnos_ausentes": 0,
      "porcentaje_pendientes": 0,
      "porcentaje_confirmados": 0,
      "porcentaje_cancelados": 0,
      "porcentaje_atendidos": 0,
      "porcentaje_ausentes": 0,
      "espera_promedio_dias": 0
    }
  ]
}
```

Campos exactos se validan contra respuesta real; Pydantic flexible o modelo alineado al JSON de prod.

### BE request

`GET .../turnos-resumen?fecha_desde=...&fecha_hasta=...` (JWT).  
Interno: GET `{DISTRIBUCION_TURNOS_RESUMEN_URL}?fecha_desde&fecha_hasta` + `Authorization: Bearer {NOVEDADES_PROF_SYNC_TOKEN}`.

Timeout: reutilizar patrón de otros fetches distribución (env opcional o default ~30s).

### Agregación (set filtrado)

- Contadores: suma de cada `turnos_*` y `total_turnos`.
- Porcentajes: `100 * sum(turnos_X) / sum(total_turnos)` (0 si denom 0).
- `espera_promedio_dias`: Σ(espera_i × total_turnos_i) / Σ(total_turnos_i).

## UI

### Ocupación (`OccupancyPage`)

- Columna `id` (numérica, legible) además de agenda/día/horario/estado.

### Indicadores (`IndicadoresOcupacionPage`)

- Bloque **Resumen de turnos** debajo del import CSV si existe en la rama; si no, debajo de KPIs/torta.
- Estados: idle → loading (spinner local) → datos | empty | error (mensaje corto).
- No deshabilitar ni esperar para el resto de la página.

## Placement note (rama `consultorios`)

Puede no existir UI CSV de turnos; el diseño ancla el bloque relativo a KPIs/torta y, si hay import, debajo de ese import.

## Config

| Var | Uso |
|-----|-----|
| `DISTRIBUCION_TURNOS_RESUMEN_URL` | Base/URL del endpoint externo |
| `NOVEDADES_PROF_SYNC_TOKEN` | Bearer (existente) |
| (opcional) timeout dedicado | si el proyecto ya tiene patrón; si no, default en código |

Documentar en `.env.prod.example` + runbook.

## Testing

- BE: mock httpx → 200 con detalle; timeout/5xx → 502/504 genérico sin filtrar token.
- FE: join excluye ids no presentes; filtros no disparan fetch; cambio de mes sí.
- Ocupación: response incluye `id`; columna renderiza.

## Security

- Token solo en BE.
- JWT en ruta clínica.
- Errores genéricos al cliente (sin body externo crudo con secretos).
