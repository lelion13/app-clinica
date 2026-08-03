# Delta: novedades

## ADDED Requirements

### Requirement: Verificación de producción al cargar

On the Carga page, before creating a module assignment and/or novedad, and before confirming an update of `fecha_realizacion`, the system MUST verify production for that professional and date via a **backend proxy** to the external `tiene-produccion` API (Bearer = Novedades professional sync token; URL from `NOVEDADES_BONOS_TIENE_PRODUCCION_URL`). The query MUST use `fecha` = selected realization date and `codprof` = catalog `CODPROF` (not internal id).

The check MUST run when the user confirms the action (submit Cargar / confirm fecha edit), for roles `admin` and `jefe_medico`. If the external result is false, the UI MUST show: “El profesional no tiene producción en esa fecha. No se puede cargar módulo ni novedad para ese día.” and MUST NOT send the create/update. If the proxy/external call fails, the UI MUST block the action (fail-closed) with an error modal. The create/update backend endpoints are NOT required to re-validate this rule in this change.

#### Scenario: Sin producción

- GIVEN fecha y profesional con CODPROF conocidos
- AND el proxy responde `tiene_produccion: false`
- WHEN el usuario pulsa Cargar
- THEN MUST ver el modal de sin producción
- AND MUST NOT crear módulo ni novedad

#### Scenario: Con producción

- GIVEN proxy responde true
- WHEN pulsa Cargar con payload válido
- THEN MUST continuar el flujo de alta normal

#### Scenario: API caído

- GIVEN el proxy/externo falla
- WHEN pulsa Cargar
- THEN MUST bloquearse la carga con modal de error

#### Scenario: Editar fecha

- GIVEN carga existente
- WHEN confirma nueva fecha y el proxy responde false
- THEN MUST NO actualizar la fecha
