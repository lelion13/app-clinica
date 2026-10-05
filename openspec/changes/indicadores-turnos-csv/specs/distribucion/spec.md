# Delta Spec: distribucion — indicadores-turnos-csv

## ADDED Requirements

### Requirement: Import CSV de turnos en Indicadores

`/indicadores-ocupacion` MUST ofrecer **Importar datos de turnos** (upload CSV). El backend MUST persistir el archivo en DB con `filename`, período derivado del min–max de `Fecha Turno`, y filas. Varios imports MUST poder coexistir.

Match MUST ser exacto normalizado entre CSV `Nombre` y `nombre_agenda` del sync. Si alguna fila no matchea, MUST rechazar el import entero y devolver detalle (fila + nombre) para modal UI.

JWT `admin`|`operador`.

#### Scenario: Import rechazado

- **Given** CSV con un Nombre sin `nombre_agenda` equivalente en sync
- **When** import
- **Then** 422 y no se persiste; UI muestra modal con filas/nombres sin match

### Requirement: KPIs de turnos bajo la torta

Debajo de la torta/tops, MUST mostrar: cantidad turnos (AT+AU), ausentes (AU), % ausentismo, promedio minutos presente→atendido (solo AT con fechas), promedio días espera reserva→turno (solo AT con fechas).

Los KPIs MUST filtrarse por el período Día|Mes de la UI (`Fecha Turno`) y por ubicación/consultorio/especialidad/médico usando la agenda matcheada en el sistema (sync + mapeo room).

#### Scenario: Filtro mes

- **Given** import con turnos en sep-2026
- **When** Indicadores period=month 2026-09
- **Then** solo cuentan filas con Fecha Turno en ese mes
