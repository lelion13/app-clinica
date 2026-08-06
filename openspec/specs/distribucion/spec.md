# Distribución Specification

## Purpose

Dominio de distribución de consultorios: sync de ocupación (horarios activos), materialización de agenda ocupación, mapeo `id_agenda` → consultorio, vínculo ubicación↔ocupación `(id_dominio, tipo)`, y UI de grillas asociadas.

## Traceability (source of truth vs archives)

| Capacidad | Spec estable (esta) | Archive origen |
|-----------|---------------------|----------------|
| Sync Ocupación `/ocupacion`, env, tabla, split `nombre_agenda`, filtros/indicadores grilla sync | § Sync y Ocupación | `2026-08-06-distribucion-ocupacion` |
| API `agenda/events` + `filter-options` (materialización) | § Agenda API | `2026-08-06-agenda-ocupacion-sync` |
| Mapeo `id_agenda`→room + columnas consultorio / Sin consultorio | § Mapeo | `2026-08-06-mapeo-agenda-consultorio` |
| `locations.tipo` + unique par + filtro location dominio+tipo | § Ubicaciones | `2026-08-06-locations-tipo` |
| UI Agenda ocupación (planilla, filtros una fila, modal, viewport) | § UI Agenda | `2026-08-06-agenda-ocupacion-ui` |

**Regla anti-ambigüedad:** si un archive antiguo dice FullCalendar/popover/multi-select o PK=`id_dato`, **prevalece esta spec estable**. Los deltas archivados son histórico; no reabrir esos changes para “arreglar” texto contradictorio sin actualizar esta spec.

---

## Requirements

### Requirement: Menú Ocupación

El sistema MUST mostrar un ítem **Ocupación** bajo Distribución, path `/ocupacion`, visible para `admin` y `operador`. **Ocupación semanal** MUST permanecer como ítem distinto.

#### Scenario: Operador ve ambos ítems

- **Given** usuario `operador`
- **When** abre el menú Distribución
- **Then** ve **Ocupación semanal** y **Ocupación** como entradas distintas

### Requirement: Persistencia y sync de horarios activos

El backend MUST persistir cada fila del endpoint externo en `ocupacion_horario_activo` con:

- PK **serial local** (no colapsar por `id_dato`: el API puede repetir `id_dato`)
- `payload` JSONB = fila externa tal cual
- columnas derivadas `tipo` / `especialidad_agenda` / `medico` (+ campos de filtro/vigencia según implementación)

`POST /api/v1/distribucion/ocupacion/horarios-activos/sync` MUST, tras GET externo OK, wipe+reload en una transacción. Si el GET falla, MUST NOT modificar la tabla (502).

`GET /api/v1/distribucion/ocupacion/horarios-activos` MUST leer de DB y filtrar `fecha_hasta >= hoy`.

Ambos endpoints MUST exigir JWT + `admin`/`operador`. El Bearer (`NOVEDADES_PROF_SYNC_TOKEN`) MUST NOT devolverse al cliente.

Env: `DISTRIBUCION_HORARIOS_ACTIVOS_URL` (+ timeout). MUST NOT eliminarse al tocar settings de otros dominios.

#### Scenario: Sync OK

- **Given** URL/token OK y upstream 200
- **When** POST sync
- **Then** la tabla refleja el payload fila-a-fila y la respuesta incluye `synced`

#### Scenario: Sync upstream fallido

- **Given** datos previos y upstream falla
- **When** POST sync
- **Then** 502 y la tabla no cambia

#### Scenario: Listado vigente

- **Given** filas con `fecha_hasta` pasada y futura
- **When** GET list
- **Then** solo filas con `fecha_hasta >= hoy`

### Requirement: Split de nombre_agenda

El backend MUST derivar `tipo`, `especialidad_agenda` y `medico` partiendo `nombre_agenda` por `" - "`. Si no hay ese separador y hay `-`, MUST partir por `-` (strip). Parte 1 → `tipo`, parte 2 → `especialidad_agenda`, resto → `medico`. Faltantes → null. La grilla Ocupación MUST NOT mostrar `nombre_agenda` crudo.

Tras cambiar el parser, MUST re-sync (Actualizar en Ocupación) para refrescar derivados.

#### Scenario: Tres partes espaciadas

- **Given** `ART - TRAUMATOLOGIA - APECECHEA …`
- **When** sync/derive
- **Then** tipo/especialidad_agenda/medico partidos correctamente

#### Scenario: Compacto con guiones

- **Given** `CMG-ECOGRAFIA-DR. BARRERA`
- **When** sync/derive
- **Then** `tipo=CMG`, `especialidad_agenda=ECOGRAFIA`, resto en `medico`

### Requirement: Grilla Ocupación (sync UI)

`/ocupacion` MUST auto-cargar al abrir, ofrecer **Actualizar** (= sync), y mostrar columnas: `id_dominio`, `tipo`, `especialidad_agenda`, `medico`, `especialidad`, `dia`, `fecha_desde`, `hora_desde`, `fecha_hasta`, `hora_hasta`, `duracion_turno`.

MUST permitir filtros multi-select por columna (OR en columna, AND entre columnas). MUST ofrecer **Indicadores** sobre filas filtradas (agrupación dominio+especialidad+medico+dia; métricas horas/turnos/sobreturnos).

### Requirement: Agenda ocupación — API de eventos

`GET /api/v1/distribucion/ocupacion/agenda/events` MUST exigir JWT `admin`|`operador` y query `start`/`end` ventana `[start, end)`.

MUST materializar un evento por ocurrencia de fila sync con `dia` válido (ES), horas parseables, y solape de `[fecha_desde, fecha_hasta]` con la ventana, en el weekday correspondiente.

Cada evento MUST incluir `start`, `end`, `title` (= medico o vacío), `resource_id`, `extended` (detalle).

MUST aceptar filtros opcionales: `location_id`, `id_dominio`, `tipo`, `especialidad`, `medico`, `dia` (listas). `especialidad` matchea `especialidad` **o** `especialidad_agenda` (casefold). Vacío = sin filtro.

`GET .../agenda/filter-options` MUST exponer valores distintos para armar filtros UI.

Filas sin `dia`/horas válidas MUST NOT generar eventos.

#### Scenario: Lunes en ventana

- **Given** fila `dia=lunes` 09:00–12:00 vigente
- **When** events cubre ese lunes
- **Then** hay evento ese día en ese rango

### Requirement: Mapeo id_agenda → consultorio

El sistema MUST persistir `id_agenda` → `room_id` con `id_agenda` único (rev `0015`).

MUST listar/agregar/quitar desde ficha consultorio (JWT admin|operador). Si ya está en otro room, MUST 409 salvo `confirm_move=true` (mueve).

MUST ofrecer lookup typeahead por médico desde snapshot sync; label `id_agenda — nombre_agenda`.

`GET .../agenda/events` MUST resolver `resource_id` = id de room o `unassigned`.

#### Scenario: Sin mapeo

- **Given** fila con `id_agenda` sin mapeo
- **When** events del día
- **Then** `resource_id` = `unassigned`

#### Scenario: Move con confirmación

- **Given** id_agenda en room A
- **When** POST a room B con `confirm_move=true`
- **Then** queda solo en B

### Requirement: Ubicación vinculada por id_dominio + tipo

MUST persistir `locations.tipo` no vacío; obligatorio en create/update. Unique activo `(id_dominio, tipo)` (rev `0016`). Placeholders migrate `PENDIENTE-{id}` editables en UI.

Filtro agenda por `location_id` MUST aplicar **id_dominio y tipo** de esa location (casefold). Labels SHOULD usar par `(id_dominio, tipo)`.

#### Scenario: Mismo dominio, distinto tipo

- **Given** dos locations `1651` + tipos distintos
- **When** filtro por una
- **Then** solo eventos de ese tipo

### Requirement: UI Agenda ocupación

Menú **Agenda ocupación** `/agenda-ocupacion` (`admin`/`operador`). Solo lectura; MUST NOT sync (sync solo en Ocupación). `/agenda` (bookings) intacta.

MUST mostrar grilla día × consultorios (+ **Sin consultorio**), horas alineadas (sin drift box-model), full-bleed + altura viewport, scroll interno, cabecera sticky, columnas ≥160px.

Filtros en **una fila** de selects (un valor o vacío=Todos): Ubicación, Día (+ nav), Tipo, Especialidad, Médico — vía `filter-options` / `events`. Sin consultorio respeta los mismos filtros.

Click bloque → modal centrado + overlay; cierra Esc / overlay / Cerrar. Título/ayuda mínimos para maximizar grilla.

#### Scenario: Filtros en una fila

- **Given** desktop
- **When** abre Agenda ocupación
- **Then** filtros en una banda compacta (sin listas checkbox altas)

#### Scenario: Cierre modal

- **Given** modal abierto
- **When** Esc o overlay
- **Then** se cierra
