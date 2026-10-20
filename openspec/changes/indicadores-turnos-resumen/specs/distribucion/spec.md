# Delta Spec: distribucion — indicadores-turnos-resumen

## ADDED Requirements

### Requirement: Occupancy rows expose horario id

The occupancy API and Ocupación UI SHALL expose the remote horario `id` for each active row returned by Actualizar sync, so clients can join external turnos data.

#### Scenario: Ocupación shows id after sync

- **WHEN** the user has synced occupancy and opens Ocupación
- **THEN** each visible row includes a non-null `id` column corresponding to the synced horario identifier

#### Scenario: Occupancy list payload includes id

- **WHEN** an authenticated client requests the occupancy list endpoint
- **THEN** each active item in the response includes an integer `id` field

### Requirement: Backend proxies turnos resumen by date range

The backend SHALL provide a JWT-protected endpoint that fetches turnos resumen from `DISTRIBUCION_TURNOS_RESUMEN_URL` using Bearer `NOVEDADES_PROF_SYNC_TOKEN`, forwarding `fecha_desde` and `fecha_hasta`, and returning a validated summary payload to the client without exposing the token.

#### Scenario: Successful proxy for a day range

- **WHEN** an authenticated client requests turnos resumen with `fecha_desde` equal to `fecha_hasta` (Día mode)
- **THEN** the backend requests the external URL with those query params and returns the summary JSON (or an equivalent validated model)

#### Scenario: Successful proxy for a month range

- **WHEN** an authenticated client requests turnos resumen with `fecha_desde` = first day and `fecha_hasta` = last day of the selected month
- **THEN** the backend performs a single external fetch for that inclusive range and returns the summary

#### Scenario: External failure does not leak secrets

- **WHEN** the external service times out or returns an error
- **THEN** the client receives a generic error status/message and no sync token or raw credential material is included

### Requirement: Indicadores loads turnos resumen asynchronously

Indicadores ocupación SHALL fetch turnos resumen only when the period mode or selected day/month changes (including initial mount), SHALL NOT block the existing occupancy KPIs/chart on that fetch, and SHALL join detalle rows where `turno_horario_id` equals occupancy `id`.

#### Scenario: Fetch on day/month change only

- **WHEN** the user changes Día date or Mes month (or loads the page with a period)
- **THEN** the client requests turnos resumen for the corresponding date range once for that selection

#### Scenario: Filters reclassify in memory

- **WHEN** the user changes agenda, weekday, horario, or estado filters after resumen data is loaded
- **THEN** the client does not re-fetch the external summary and instead recomputes the joined/aggregated metrics from the already downloaded detalle using the filtered occupancy id set

#### Scenario: Non-blocking load

- **WHEN** turnos resumen is still loading or has failed
- **THEN** occupancy indicators (torta/KPIs and any CSV import UI) remain usable
- **AND** the resumen block shows a local loading or error state

### Requirement: Turnos resumen aggregation

For the filtered set of detalle rows that match occupancy ids in scope, Indicadores SHALL display all summary metric fields from the API, aggregating as: sum of count fields; percentages recomputed from aggregated counts over aggregated `total_turnos`; `espera_promedio_dias` as a `total_turnos`-weighted average.

#### Scenario: Aggregate counts and percentages

- **WHEN** two matching detalle rows have totals 10 and 30 with confirmed 2 and 6
- **THEN** aggregated `total_turnos` is 40, aggregated confirmed is 8, and confirmed percentage is 20

#### Scenario: Weighted wait average

- **WHEN** matching rows have espera 2 with total 10 and espera 4 with total 30
- **THEN** aggregated `espera_promedio_dias` is 3.5
