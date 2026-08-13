# Delta: novedades

## ADDED Requirements

### Requirement: Verificación de producción al cargar

On the Carga page, before creating a module assignment and/or novedad, and before confirming an update of `fecha_realizacion`, the system MUST verify production for that professional and date via a **backend proxy** to the external `tiene-produccion` API (Bearer = Novedades professional sync token; URL from `NOVEDADES_BONOS_TIENE_PRODUCCION_URL`). The query MUST use `fecha` = selected realization date and `codprof` = catalog `CODPROF` (not internal id).

The check MUST run when the user confirms the action (submit Cargar / confirm fecha edit), for roles `admin` and `jefe_medico`.

If the proxy/external call **fails**, the UI MUST block the action (fail-closed) with an error modal and MUST NOT offer force-load.

If the external result is **false** on **create** (alta): see Requirement “Force-load sin producción”.

If the external result is **false** on **edit fecha**: the UI MUST block the update with a simple message and MUST NOT offer force-load. The create/update backend endpoints are NOT required to re-validate `tiene-produccion` in this change.

#### Scenario: Con producción

- GIVEN proxy responde true
- WHEN pulsa Cargar con payload válido
- THEN MUST continuar el flujo de alta normal (sin motivo/obs)

#### Scenario: API caído

- GIVEN el proxy/externo falla
- WHEN pulsa Cargar
- THEN MUST bloquearse la carga con modal de error
- AND MUST NOT mostrar el flujo de force-load

#### Scenario: Editar fecha sin producción

- GIVEN carga existente
- WHEN confirma nueva fecha y el proxy responde false
- THEN MUST NO actualizar la fecha
- AND MUST NOT ofrecer force-load con motivo

### Requirement: Force-load sin producción

When create-submit receives `tiene_produccion: false`, the UI MUST show a modal containing: the message “El profesional no tiene producción en esa fecha. No se puede cargar módulo ni novedad para ese día.”; a motivo select defaulting to empty with options **Vacaciones** and **Enfermedad** only; a mandatory observation field; buttons **Cancelar** and **Cargar**.

- **Cancelar** MUST close the modal and MUST NOT create cargas.
- **Cargar** MUST require a selected motivo and non-blank observation; then MUST create the intended module and/or novedad including the same `motivo_sin_produccion` and `observacion_sin_produccion` on each created row.
- Roles: `admin` and `jefe_medico`.

The system MUST persist those fields on `novedades_asignacion_modulo` and `novedades_novedad` and expose them on list/detail responses for Carga. Backend MUST accept optional motivo/obs on create (validate enum + non-empty obs when provided) and MUST NOT require them on every create nor re-check production server-side.

#### Scenario: Cancelar force

- GIVEN modal force visible tras `false`
- WHEN pulsa Cancelar
- THEN MUST cerrarse el modal
- AND MUST NOT crearse módulo ni novedad

#### Scenario: Cargar force incompleto

- GIVEN modal force sin motivo o sin observación
- WHEN pulsa Cargar
- THEN MUST rechazar (validación UI)
- AND MUST NOT enviar POST

#### Scenario: Cargar force OK (módulo + novedad)

- GIVEN modal force con motivo Vacaciones y observación “texto”
- AND el form pedía módulo y novedad
- WHEN pulsa Cargar
- THEN MUST crearse ambas filas
- AND ambas MUST tener el mismo motivo y observación persistidos
