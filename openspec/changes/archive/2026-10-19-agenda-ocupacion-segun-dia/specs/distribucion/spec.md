# Delta Spec: distribucion — agenda-ocupacion-segun-dia

## MODIFIED Requirements

### Requirement: Mapeo id_agenda → consultorio

(Previously: `id_agenda` único → un `room_id` para todos los días.)

El sistema MUST persistir el mapeo **`(id_agenda, weekday)` → `room_id`**, donde `weekday` es el día de la semana del bloque sync (mismo convenio 0–6 que `room_operating_hours`).

Un mismo `id_agenda` MAY tener distintos `room_id` en distintos weekdays. Weekdays sin fila de mapa MUST tratarse como Sin consultorio.

Migración desde el mapa 1:1: cada fila existente MUST expandirse a **todos** los weekdays con bloques sync parseables de ese `id_agenda`, conservando el mismo `room_id`.

`GET .../agenda/events` MUST resolver `resource_id` con el mapa del **weekday del evento** (no un room global del `id_agenda`).

La asociación agenda↔consultorio MUST NOT validar contra `room_operating_hours` en el path Consultorios salvo donde este delta exige validación (assign batch); el path DnD SÍ valida (ver Reassign / Validación).

#### Scenario: Sin mapeo ese día

- **Given** `id_agenda` con lunes mapeado a C1 y martes sin fila
- **When** events de un martes
- **Then** `resource_id` = `unassigned` para el bloque del martes

#### Scenario: Migración expand

- **Given** mapa legado Pérez→C1 y sync con lunes+martes
- **When** corre la migración
- **Then** existen filas (Pérez, lunes)→C1 y (Pérez, martes)→C1

### Requirement: Reassign agenda via Agenda ocupación (DnD)

(Previously: remapeaba el `id_agenda` completo en todos los días.)

El sistema MUST permitir reasignar **solo el weekday del día seleccionado en el calendario** mediante DnD horizontal. Persistencia al soltar vía `POST /api/v1/distribucion/ocupacion/agenda/reassign` (JWT `admin`|`operador`) incluyendo el weekday (o fecha de la que se deriva).

Movimientos: Sin consultorio ↔ consultorio y entre consultorios, **solo para ese weekday**. Otras filas `(id_agenda, otros weekdays)` MUST permanecer intactas.

La grilla MUST mostrar/mover solo agendas que tienen bloque sync en ese weekday.

#### Scenario: Asignar solo el lunes

- **Given** agenda con lunes+martes en Sin consultorio; calendario en lunes; room C1 válido ese lunes
- **When** drop en C1
- **Then** solo el lunes queda en C1; el martes sigue Sin consultorio

#### Scenario: Desasignar solo el día

- **Given** lunes y martes en C1; calendario en lunes
- **When** drop a Sin consultorio
- **Then** se borra el mapa del lunes; el martes permanece en C1

### Requirement: Validación horario box y sin solape (path reassign)

(Previously: validaba todos los weekdays de la agenda.)

Al asignar/mover en AO (`target_room_id` no null), el backend MUST validar **únicamente el weekday reasignado**: cobertura en `room_operating_hours` y sin solape con otras agendas del room ese weekday (half-open; excluir el propio `(id_agenda, weekday)`). Fallo → no persistir + error detallado.

#### Scenario: Martes conflictivo no bloquea lunes

- **Given** agenda OK el lunes en C1 y con solape el martes en C1
- **When** reassign del lunes a C1
- **Then** el lunes se acepta (no se evalúa el martes en ese request)

### Requirement: UI Agenda ocupación

(Previously: columnas consultorio sin orden numérico ni scroll H / sticky condicional.)

Además de lo estable: columnas de consultorios MUST ordenarse por número extraído del `code` (C1, C2, … C10); códigos sin número MUST ir al final.

Si las columnas no caben, MUST haber scroll horizontal. Durante un drag cerca del borde izquierdo/derecho, la grilla MUST auto-desplazarse horizontalmente.

La columna **Sin consultorio** MUST quedar fija a la izquierda mientras haya ítems en ella; si está vacía, MUST desplazarse con el resto.

### Requirement: UI Consultorios — grilla y modales

(Previously: modal Agendas asociaba el `id_agenda` completo a un room.)

El modal **Agendas** MUST:

- **Assign:** asociar a ese room solo los weekdays de la agenda que aún están Sin consultorio. MUST NOT modificar weekdays ya mapeados a otros rooms. MUST ser todo-o-nada: si algún weekday pendiente falla validación horario/solape, MUST NOT persistir ninguno y MUST mostrar modal de conflicto.
- **List:** si **todos** los weekdays sync de la agenda están en ese room → una fila con el nombre (sin sufijo de día). Si solo algunos → una fila por weekday en ese room con label `{nombre} - {día}` (ej. `Dr. Pérez - lunes`).
- **Unassign:** con fila full → quitar todos los weekdays de esa agenda en ese room. Con fila parcial → quitar solo ese weekday.

#### Scenario: Assign no pisa otro room

- **Given** lunes en C2; martes Sin consultorio
- **When** assign a C1 desde Consultorios
- **Then** solo el martes pasa a C1; el lunes permanece en C2

#### Scenario: Assign con conflicto

- **Given** dos días pendientes y uno solapa en C1
- **When** assign a C1
- **Then** modal de conflicto y cero filas nuevas

#### Scenario: Label parcial

- **Given** solo lunes en C1 (martes en otro lado o sin mapa)
- **When** abre Agendas de C1
- **Then** ve `… - lunes` (no una sola fila sin día)

## ADDED Requirements

### Requirement: Confirmaciones robo y desasignar (weekday)

Robo: si el `(id_agenda, weekday)` ya está en otro room, UI confirm + `confirm_move`; sin confirm → 409. Desasignar en AO: UI confirm + `confirm_unassign`; sin validar horario/solape; solo ese weekday.
