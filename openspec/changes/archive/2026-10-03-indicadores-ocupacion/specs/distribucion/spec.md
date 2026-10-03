# Delta for distribucion — indicadores-ocupacion

## ADDED Requirements

### Requirement: Menú Indicadores ocupación

El sistema MUST mostrar bajo Distribución el ítem **Indicadores ocupación** con path `/indicadores-ocupacion`, visible a roles `admin` y `operador`.

MUST coexistir con **Estadística** (`/estadisticas`); este change MUST NOT alterar el cálculo por bookings de Estadística.

#### Scenario: Operador ve la entrada

- **Given** usuario `operador`
- **When** abre el menú Distribución
- **Then** ve **Indicadores ocupación** además de las entradas existentes

### Requirement: API indicadores de ocupación (sync)

El sistema MUST exponer un endpoint protegido JWT (`admin`|`operador`), p. ej. `GET /api/v1/distribucion/ocupacion/indicadores`, que calcule métricas para un `date` (día calendario de negocio).

**Inclusión de consultorios:** todos con `deleted_at IS NULL`, filtrados opcionalmente por `location_id` y/o `room_id`.

**Denominador (`enabled_hours`):** suma de horas de `room_operating_hours` cuyo `weekday` corresponde al día (misma convención JS que el resto del sistema), solo para rooms **con al menos una franja ese weekday**. Rooms sin franja ese día MUST NOT aportar al denominador ni a la torta; MUST listarse como `rooms_without_hours`.

**Numerador (`occupied_hours`):** suma de duraciones de bloques sync materializables ese día (mismo criterio de `dia`/vigencia/`hora_desde`–`hora_hasta` que Agenda ocupación) cuya `id_agenda` está mapeada a un room incluido. MUST NOT recortar el bloque al horario operativo. Agendas sin mapeo MUST NOT sumar. Filtros opcionales `especialidad` y `medico` MUST aplicarse solo al numerador (`especialidad` OR `especialidad_agenda`, case-insensitive).

**Porcentaje:** `occupied_hours / enabled_hours * 100` cuando `enabled_hours > 0`; MAY ser > 100. Si `enabled_hours = 0` (todos sin horario o sin rooms), MUST reportar ocupación nula/ indeterm. de forma segura (sin división por cero) y torta vacía o mensaje.

La respuesta MUST incluir al menos: `occupied_hours`, `enabled_hours`, `free_hours` (max(0, enabled−occupied) para la porción “libre” de la torta; si occupied>enabled la porción libre MAY ser 0 y el % mostrarse aparte), `occupancy_percent`, `rooms_without_hours`, y conteos útiles.

#### Scenario: Room sin agenda mapeada

- **Given** un room con horario ese día y sin `id_agenda`
- **When** se calculan indicadores del día
- **Then** aporta sus horas al denominador y 0 al numerador

#### Scenario: Room sin horario ese weekday

- **Given** un room sin `room_operating_hours` para ese weekday
- **When** se calculan indicadores
- **Then** aparece en `rooms_without_hours` y no altera la torta

#### Scenario: Bloque sync más largo que el horario del box

- **Given** bloque sync 4h y horario operativo 3h ese día
- **When** se calcula
- **Then** el numerador suma 4h y el % puede superar 100

#### Scenario: Filtro médico

- **Given** denom de todos los rooms de una ubicación
- **When** se filtra por un médico
- **Then** el numerador solo incluye bloques de ese médico; el denominador no se reduce por el filtro médico

### Requirement: UI Indicadores ocupación

La pantalla `/indicadores-ocupacion` MUST:

- Al abrir, cargar indicadores del **día de hoy** para todos los consultorios (según reglas de la API).
- Ofrecer filtros en una banda: **fecha**, **ubicación**, **consultorio**, **especialidad**, **médico** (select un valor o Todos).
- Mostrar una **torta** global ocupado vs libre con porcentajes visibles (y % de ocupación, incluso >100%).
- Mostrar horas absolutas ocupadas / habilitadas.
- Mostrar aviso/lista de consultorios **sin horario** ese día.
- Ser solo lectura; MUST NOT invocar sync.

#### Scenario: Carga inicial

- **Given** admin en la ruta
- **When** abre la página
- **Then** ve la torta del día actual sin filtros (Todos)
