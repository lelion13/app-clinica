# Delta Spec: distribucion — agenda-ocupacion-dnd

## ADDED Requirements

### Requirement: Reassign agenda via Agenda ocupación (DnD)

El sistema MUST permitir reasignar el mapeo persistente `id_agenda` → `room_id` desde la UI **Agenda ocupación** mediante drag-and-drop **horizontal** (cambio de columna únicamente). Las horas del bloque MUST permanecer las del sync; MUST NOT permitir drag vertical ni resize que altere horarios.

Movimientos permitidos:
- `Sin consultorio` → consultorio
- consultorio → otro consultorio
- consultorio → `Sin consultorio` (desasignar)

El drop MUST respetar los **filtros actuales** de la vista: solo columnas visibles son destinos válidos.

Persistencia MUST ocurrir al soltar (tras confirmaciones cuando apliquen), vía API dedicada de reassign (JWT `admin`|`operador`).

#### Scenario: Asignar desde Sin consultorio

- **Given** un bloque en Sin consultorio cuyo `id_agenda` no tiene room
- **And** el room destino tiene horario que cubre todos los intervalos de esa agenda en sync y sin solapes
- **When** el usuario suelta el bloque en esa columna
- **Then** el mapeo `id_agenda`→room se persiste y todas las ocurrencias de esa agenda pasan a ese consultorio

#### Scenario: Solo columna

- **Given** un bloque 10:00–12:00
- **When** el usuario intenta arrastrar en vertical
- **Then** la hora no cambia (solo se permite cambio de columna)

### Requirement: Validación horario box y sin solape (path reassign)

Al asignar o mover a un `target_room_id` (no null), el backend MUST validar **todos** los weekdays en los que el sync tiene bloques parseables para ese `id_agenda`:

1. Cada intervalo `[hora_desde, hora_hasta)` MUST estar cubierto por el horario operativo (`room_operating_hours`) del room destino ese weekday.
2. Cada intervalo MUST NOT solapar intervalos de **otras** agendas ya mapeadas a ese room (materializadas desde sync para ese weekday). El propio `id_agenda` MUST excluirse del check de solape.
3. Intervalos adyacentes (fin = inicio) MUST NOT considerarse solape (modelo half-open).

Si alguna validación falla, MUST NOT persistir el mapeo y MUST devolver error con detalle usable en UI (weekday, horario, conflicto si aplica).

Esta validación MUST aplicar al path de reassign/DnD. El modal **Agendas** en Consultorios MAY seguir sin estas reglas (comportamiento existente preservado).

#### Scenario: Fuera de horario

- **Given** agenda con bloque martes 18:00–20:00 y room con hours martes solo hasta 17:00
- **When** reassign a ese room
- **Then** se rechaza sin persistir

#### Scenario: Solape

- **Given** room con agenda A 09:00–11:00 los lunes y agenda B unassigned 10:00–12:00 los lunes
- **When** reassign B a ese room
- **Then** se rechaza por solape

#### Scenario: Un weekday falla, otros OK

- **Given** agenda con bloques lunes (OK en box) y miércoles (fuera de hours del box)
- **When** reassign
- **Then** se rechaza (MUST validar todos los weekdays)

### Requirement: Confirmaciones robo y desasignar

Si el `id_agenda` ya está mapeado a **otro** room y el usuario dropea en un room distinto, la UI MUST pedir confirmación antes de reenviar con `confirm_move=true`. Sin confirmación, el backend MUST responder conflicto (409) y MUST NOT mover.

Al dropear en **Sin consultorio**, la UI MUST pedir confirmación de desasignar. Tras confirmar, el backend MUST eliminar el mapeo de ese `id_agenda` (cualquier room). Desasignar MUST NOT exigir validación de horario ni solape.

#### Scenario: Robo con confirm

- **Given** agenda en room A
- **When** drop en room B y el usuario confirma
- **Then** queda solo en B

#### Scenario: Desasignar

- **Given** agenda en room A
- **When** drop en Sin consultorio y confirma
- **Then** `resource_id` = unassigned y no hay fila de mapa para ese `id_agenda`

### Requirement: Feedback de rechazo DnD

Si el reassign falla por validación (horario/solape) u otro error de negocio, la UI MUST mostrar un **modal** con el motivo detallado y MUST devolver el bloque a su columna original (sin mapeo cambiado).

#### Scenario: Modal de error

- **Given** drop inválido por solape
- **When** la API responde error
- **Then** el usuario ve modal con detalle y el bloque sigue en el origen

## MODIFIED Requirements

### Requirement: UI Agenda ocupación

MODIFIED: la UI Agenda ocupación deja de ser estrictamente **solo lectura** respecto del mapeo agenda↔consultorio.

MUST continuar:
- sin sync propio (sync solo en Ocupación);
- filtros en una fila;
- grilla día × consultorios + Sin consultorio;
- click → modal detalle.

MUST además permitir drag-and-drop de bloques entre columnas según requisitos ADDED (reassign/unassign con validaciones y confirmaciones).

#### Scenario: Filtros en una fila

- **Given** desktop
- **When** abre Agenda ocupación
- **Then** filtros en una banda compacta (sin listas checkbox altas)

#### Scenario: DnD con filtros

- **Given** filtro de ubicación que oculta room X
- **When** el usuario arrastra un bloque
- **Then** no puede soltar en X (no visible)
