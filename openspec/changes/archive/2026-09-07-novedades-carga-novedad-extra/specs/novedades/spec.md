# Delta Spec: novedades-carga-novedad-extra

## ADDED Requirements

### Requirement: Novedad extra en Carga (módulo sin producción)

On the Carga page, when the selected módulo has `produccion=false`, the UI MUST show an optional checkbox labeled **Novedad extra** after the módulo value (read-only) label. Default MUST be unchecked.

When the selected módulo has `produccion=true` or no módulo is selected, the checkbox MUST be hidden and its state MUST be cleared.

When **Novedad extra** becomes checked:
- The novedad (tipo/horas) controls MUST be cleared and MUST NOT accept input for that submit.
- The create submit MUST NOT call the external `tiene-produccion` API.
- The UI MUST open the same **Force-load sin producción** modal (same message, Vacaciones/Enfermedad, mandatory observation, Cancelar/Cargar).
- On successful **Cargar** from that modal, the system MUST create only the **módulo** assignment with `motivo_sin_produccion` and `observacion_sin_produccion`; it MUST NOT create a novedad row.
- No additional persisted flag beyond those sin-producción fields is required.

When **Novedad extra** is unchecked and the módulo has `produccion=false`, Requirement “Verificación de producción en Carga — flag módulo” MUST apply unchanged (skip external check; módulo and/or novedad allowed as today).

#### Scenario: Checkbox visible solo sin prod

- GIVEN módulo M con `produccion=false` seleccionado
- WHEN admin/jefe ve el form de Carga
- THEN MUST ver el checkbox Novedad extra destildado después del valor del módulo

#### Scenario: Cambio a módulo con prod limpia

- GIVEN Novedad extra tildado sobre módulo sin prod
- WHEN selecciona un módulo con `produccion=true`
- THEN MUST ocultarse el checkbox
- AND su estado MUST quedar limpio

#### Scenario: Novedad extra fuerza modal sin API

- GIVEN módulo sin prod y Novedad extra tildado
- WHEN pulsa Cargar novedad
- THEN MUST NOT llamar `GET .../bonos/tiene-produccion`
- AND MUST abrir el modal force-load
- AND el bloque de novedad horas MUST estar vacío y no usable

#### Scenario: Cargar force solo módulo

- GIVEN modal force abierto vía Novedad extra con motivo y observación válidos
- WHEN pulsa Cargar
- THEN MUST crearse solo la asignación de módulo con motivo/obs
- AND MUST NOT crearse novedad de horas

#### Scenario: Sin Novedad extra sigue skip

- GIVEN módulo sin prod y Novedad extra destildado
- WHEN carga módulo (con o sin novedad)
- THEN MUST NOT llamar el proxy
- AND MUST permitir el POST directo como hoy

## MODIFIED Requirements

### Requirement: Verificación de producción en Carga — flag módulo

(Previously: any carga including a módulo with `produccion=false` skipped the external check unconditionally.)

When creating a carga that includes a **módulo** with `produccion=false` and **Novedad extra is not checked**, the UI MUST NOT call the external `tiene-produccion` check for that submit (módulo and/or novedad as today).

When **Novedad extra is checked**, Requirement “Novedad extra en Carga (módulo sin producción)” MUST apply instead (force-load modal without external call; módulo only).

When the carga is only a novedad, or the selected módulo has `produccion=true`, Requirements “Verificación de producción al cargar” and “Force-load sin producción” MUST apply.

#### Scenario: Carga módulo sin producción propia (sin novedad extra)

- GIVEN módulo M con `produccion=false` y Novedad extra destildado
- WHEN admin/jefe carga solo M (o M + novedad) en una fecha
- THEN MUST NOT llamar `GET .../bonos/tiene-produccion` y MUST permitir el POST

#### Scenario: Carga solo novedad

- GIVEN formulario sin módulo
- WHEN se carga solo novedad
- THEN MUST verificar producción externa
