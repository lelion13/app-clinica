# Delta for distribucion / consulting-rooms

## ADDED Requirements

### Requirement: Mapeo id_agenda → consultorio

El sistema MUST persistir asociaciones `id_agenda` → `room_id` con `id_agenda` único.

MUST permitir listar/agregar/quitar desde el consultorio (JWT admin|operador).

Si `id_agenda` ya está en otro consultorio, MUST responder conflicto salvo `confirm_move=true`, que MUST moverlo.

MUST ofrecer lookup typeahead por médico desde el snapshot sync; cada opción MUST etiquetarse `id_agenda — nombre_agenda`.

#### Scenario: Move con confirmación

- **Given** id_agenda 10 mapeado al room A
- **When** se POST a room B con confirm_move=true
- **Then** queda solo en B

### Requirement: Agenda ocupación por consultorio

`GET .../agenda/events` MUST resolver `resource_id` = room id o `unassigned`.

La UI Agenda ocupación MUST mostrar, para un día y ubicación, columnas de consultorios de esa ubicación más **Sin consultorio**, con bloques del sync.

#### Scenario: Sin mapeo

- **Given** fila sync con id_agenda sin mapeo
- **When** se listan events del día
- **Then** el evento tiene resource_id `unassigned`
