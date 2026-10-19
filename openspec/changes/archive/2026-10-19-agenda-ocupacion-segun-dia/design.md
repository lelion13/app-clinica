# Design: agenda-ocupacion-segun-dia

## Data model

`consulting_room_id_agenda`:

- Antes: PK `id_agenda` → `room_id`.
- Después: PK `(id_agenda, weekday)` → `room_id` (`weekday` int 0–6, mismo convenio que `room_operating_hours` / reassign JS).

Migración:

1. Añadir `weekday` (nullable temporal).
2. Por cada fila: insertar N filas = weekdays con bloques parseables en sync para ese `id_agenda`.
3. Si un `id_agenda` no tiene días en sync: una fila con weekday sentinel o conservar un weekday placeholder — **preferir** expandir solo weekdays sync; si cero, dejar una fila weekday=`-1` **no**: mejor documentar y crear filas solo cuando hay días; agendas sin sync quedan sin mapa hasta reassign.
4. Drop PK vieja; PK nueva `(id_agenda, weekday)`; `weekday` NOT NULL.

Rationale: evita inventar días que no existen en sync.

## API

### Reassign (AO)

`POST .../ocupacion/agenda/reassign`:

- Request: `id_agenda`, `weekday` (o derivar de `date` del calendario UI), `target_room_id` | null, `confirm_move`, `confirm_unassign`.
- Assign/move: validar **solo** ese weekday (hours + overlap).
- Unassign: borrar fila `(id_agenda, weekday)` únicamente.
- Response: estado de ese par.

### Consultorios id-agendas

- List: devolver entradas con `id_agenda` + `weekday` (+ label día); UI agrupa full vs parcial.
- PUT/batch assign: para cada agenda elegida, calcular weekdays sync aún sin mapa; validar todos vs room; si alguno falla → 409 + detalle, sin writes; si OK → insert todas.
- Delete: por `(id_agenda, weekday)` o “todos los weekdays de id_agenda en este room” cuando la fila UI es full.

### Events

Al materializar evento de un día concreto, `resource_id` = room del mapa `(id_agenda, weekday_de_ese_día)` o `unassigned`.

Indicadores (si usan mapa): contar ocupación solo si existe mapa para el weekday del bloque.

## Frontend

### Agenda ocupación

- Filtrar bloques al weekday del día seleccionado.
- DnD envía ese weekday.
- Sort rooms: parse trailing/embedded number from `code`; non-numeric last.
- Container `overflow-x: auto`; durante drag, si pointer cerca de bordes izq/der, `scrollLeft` auto.
- Columna Sin consultorio: `position: sticky; left: 0` solo si `unassignedCount > 0`.

### Consultorios Agendas modal

- Full: una fila nombre; unassign = todos los weekdays de esa agenda en el room.
- Parcial: filas `nombre - lunes`; unassign = ese weekday.
- Assign: solo pendientes; errores → modal (reutilizar patrón conflicto).

## Tests

- Migración expand.
- Reassign lunes no toca martes.
- Validación solo weekday.
- Consultorios assign parcial OK / conflicto all-or-nothing.
- Unassign un día vs full.
- Events resource_id por weekday.

## Learned (prod migration)

**Síntoma (VPS):** `alembic upgrade head` en `0032` → `UniqueViolation` PK `consulting_room_id_agenda_pkey` Key `(id_agenda)=(10929)` al insertar el 2º weekday.

**Causa:** se expandían N filas por agenda con la PK antigua aún en solo `id_agenda`.

**Fix:** en `upgrade()`, dropear PK `id_agenda` **antes** del DELETE/INSERT de expansión; luego `weekday NOT NULL` + PK `(id_agenda, weekday)`.

**Regla:** migraciones que cambian cardinalidad de clave (1 fila → N) MUST relajar/reemplazar la constraint única **antes** de insertar las filas nuevas.
