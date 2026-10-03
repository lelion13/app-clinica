# Delta for distribucion — dashboard-estadisticas

## ADDED Requirements

### Requirement: Menú Estadística

El sistema MUST mostrar bajo Distribución el ítem **Estadística** con path `/estadisticas`, visible a `admin` y `operador`.

MUST coexistir con **Indicadores ocupación**; los cálculos MUST NOT compartirse (fuentes distintas).

### Requirement: API stats summary (asignaciones semanales)

El sistema MUST exponer `GET /api/v1/stats/summary` (JWT `admin`|`operador`) con:

- Query obligatoria de rango `start_date` / `end_date`
- Filtros opcionales: ubicaciones, consultorios, profesionales, especialidades

**Denominador:** horas de `room_operating_hours` en el rango para rooms incluidos.

**Numerador:** horas de `room_weekly_assignments` (no eliminadas) proyectadas según cuántas veces cae cada weekday en el rango. Filtro de especialidad MUST restringir el numerador sin reducir el denominador.

La respuesta MUST incluir % ocupación, horas para torta, serie por día de semana y rankings útiles.

#### Scenario: Sin asignaciones

- **Given** rooms con horario y sin weekly assignments
- **When** se pide summary
- **Then** ocupación 0% (si hay horas habilitadas)

### Requirement: UI Estadística

`/estadisticas` MUST permitir elegir rango y filtros, calcular vía API, y mostrar torta + KPIs (y gráficos auxiliares según implementación).
