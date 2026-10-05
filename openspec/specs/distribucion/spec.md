# Distribución Specification

## Purpose

Dominio de distribución de consultorios: sync de ocupación (horarios activos), materialización de agenda ocupación, mapeo `id_agenda` → consultorio, vínculo ubicación↔ocupación `(id_dominio, tipo)`, UI de grillas, e indicadores/estadísticas de ocupación.

## Traceability (source of truth vs archives)

| Capacidad | Spec estable (esta) | Archive origen |
|-----------|---------------------|----------------|
| Sync Ocupación `/ocupacion`, env, tabla, split `nombre_agenda`, filtros/indicadores grilla sync | § Sync y Ocupación | `2026-08-06-distribucion-ocupacion` |
| API `agenda/events` + `filter-options` (materialización) | § Agenda API | `2026-08-06-agenda-ocupacion-sync` |
| Mapeo `id_agenda`→room + columnas consultorio / Sin consultorio | § Mapeo | `2026-08-06-mapeo-agenda-consultorio` (+ UI/batch `2026-10-03-consultorios-ui`) |
| `locations.tipo` + unique par + filtro location dominio+tipo | § Ubicaciones | `2026-08-06-locations-tipo` |
| UI Agenda ocupación (planilla, filtros una fila, modal, viewport) | § UI Agenda | `2026-08-06-agenda-ocupacion-ui` |
| UI Consultorios (grilla, modales, horarios, sin menú Horarios) | § UI Consultorios | `2026-10-03-consultorios-ui` |
| Indicadores ocupación (sync, Día\|Mes, torta, tops; filtros payload; medico sync) | § Indicadores ocupación | `2026-10-03-indicadores-ocupacion` + `2026-10-05-indicadores-ocupacion-ui` |
| Estadística (asignaciones semanales, rango) | § Estadística | `2026-10-03-dashboard-estadisticas` |

**Regla anti-ambigüedad:** si un archive antiguo dice FullCalendar/popover/multi-select, PK=`id_dato`, o “Estadística = bookings”, **prevalece esta spec estable**. Los deltas archivados son histórico.

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
- columnas derivadas `tipo` / `especialidad_agenda` / `medico` (este último desde `medico_responsable_equipo` del payload; + campos de filtro/vigencia según implementación)

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

El backend MUST derivar `tipo` y `especialidad_agenda` partiendo `nombre_agenda` por `" - "`. Si no hay ese separador y hay `-`, MUST partir por `-` (strip). Parte 1 → `tipo`, parte 2 → `especialidad_agenda`. Faltantes → null. La grilla Ocupación MUST NOT mostrar `nombre_agenda` crudo.

La columna **`medico`** MUST completarse desde el campo del payload **`medico_responsable_equipo`** (strip; vacío/ausente → null). MUST NOT usar el resto de `nombre_agenda` para `medico`.

Tras cambiar el parser o la fuente de `medico`, MUST re-sync (Actualizar en Ocupación) para refrescar derivados.

#### Scenario: Tres partes espaciadas

- **Given** `nombre_agenda` = `ART - TRAUMATOLOGIA - APECECHEA …` y `medico_responsable_equipo` = `APECECHEA …`
- **When** sync/derive
- **Then** `tipo=ART`, `especialidad_agenda=TRAUMATOLOGIA`, `medico` = valor de `medico_responsable_equipo`

#### Scenario: Compacto con guiones

- **Given** `CMG-ECOGRAFIA-DR. BARRERA` y sin `medico_responsable_equipo`
- **When** sync/derive
- **Then** `tipo=CMG`, `especialidad_agenda=ECOGRAFIA`, `medico` = null (no el resto del nombre)

#### Scenario: medico_responsable_equipo

- **Given** `nombre_agenda` = `00.TOTEM - PB - CONSULTORIOS` y `medico_responsable_equipo` = `LOPEZ JUAN`
- **When** sync
- **Then** la columna `medico` de la grilla muestra `LOPEZ JUAN`

### Requirement: Grilla Ocupación (sync UI)

`/ocupacion` MUST auto-cargar al abrir, ofrecer **Actualizar** (= sync), y mostrar columnas: `id_dominio`, `tipo`, `especialidad_agenda`, `medico`, `especialidad`, `dia`, `fecha_desde`, `hora_desde`, `fecha_hasta`, `hora_hasta`, `duracion_turno`.

MUST permitir filtros multi-select por columna (OR en columna, AND entre columnas). MUST ofrecer **Indicadores** sobre filas filtradas (agrupación dominio+especialidad+medico+dia; métricas horas/turnos/sobreturnos).

### Requirement: Agenda ocupación — API de eventos

`GET /api/v1/distribucion/ocupacion/agenda/events` MUST exigir JWT `admin`|`operador` y query `start`/`end` ventana `[start, end)`.

MUST materializar un evento por ocurrencia de fila sync con `dia` válido (ES), horas parseables, y solape de `[fecha_desde, fecha_hasta]` con la ventana, en el weekday correspondiente.

Cada evento MUST incluir `start`, `end`, `title` (= medico o vacío), `resource_id`, `extended` (detalle).

MUST aceptar filtros opcionales: `location_id`, `id_dominio`, `tipo`, `especialidad`, `medico`, `dia` (listas). `especialidad` MUST matchear solo `payload.especialidad` (MUST NOT `especialidad_agenda`). `medico` MUST matchear `payload.medico_responsable_equipo` (fallback legado `payload.medico`). Vacío = sin filtro.

`GET .../agenda/filter-options` MUST exponer valores distintos para armar filtros UI:
- `especialidad`: solo `payload.especialidad` (no vacíos)
- `medico`: solo `payload.medico_responsable_equipo` (fallback `payload.medico`)
- demás dimensiones según implementación

Filas sin `dia`/horas válidas MUST NOT generar eventos.

#### Scenario: Lunes en ventana

- **Given** fila `dia=lunes` 09:00–12:00 vigente
- **When** events cubre ese lunes
- **Then** hay evento ese día en ese rango

#### Scenario: Filtro especialidad payload-only

- **Given** bloque con `especialidad_agenda` coincidente y `payload.especialidad` distinto
- **When** filtro especialidad = valor de `especialidad_agenda`
- **Then** ese bloque MUST NOT listarse en events

### Requirement: Mapeo id_agenda → consultorio

El sistema MUST persistir `id_agenda` → `room_id` con `id_agenda` único (rev `0015`).

MUST listar/agregar/quitar desde ficha **Consultorios** (JWT admin|operador), vía modal Agendas con draft hasta Aceptar. `PUT /api/v1/consulting-rooms/{room_id}/id-agendas` MUST replace atómico (todo-o-nada). Si un ítem ya está en otro room y `confirm_move` es false, MUST 409 sin aplicar el batch. Endpoints unitarios POST/DELETE MAY permanecer.

MUST ofrecer lookup typeahead por médico desde snapshot sync; label `id_agenda — nombre_agenda`. Cada ítem del lookup MUST incluir `current_room_id` / `current_room_code` (null si no mapeado a room activo).

`GET .../agenda/events` MUST resolver `resource_id` = id de room o `unassigned`.

La asociación agenda↔consultorio MUST NOT validar contra `room_operating_hours` (son independientes).

#### Scenario: Sin mapeo

- **Given** fila con `id_agenda` sin mapeo
- **When** events del día
- **Then** `resource_id` = `unassigned`

#### Scenario: Move con confirmación

- **Given** id_agenda en room A
- **When** PUT batch a room B con ese ítem y `confirm_move=true`
- **Then** queda solo en B

#### Scenario: Lookup muestra room actual

- **Given** agenda 100 asociada al room código `C3`
- **When** lookup encuentra esa agenda
- **Then** el ítem incluye `current_room_id` y `current_room_code=C3`

### Requirement: UI Consultorios — grilla y modales

`/consultorios` MUST, al abrir (JWT `admin`|`operador`), cargar consultorios en grilla con columnas **Ubicación** y **Nombre** (`code`), filtro select ubicación (**Todas** o una), y acciones por fila **Editar**, **Agendas**, **Horarios**, **Eliminar** (`window.confirm`).

**Agregar** MUST abrir modal ubicación + código. Modales Agregar/Editar/Agendas/Horarios MUST ser draft hasta **Aceptar**; **Cancelar** MUST NOT persistir. Solo un modal abierto a la vez.

**Editar** MUST `PATCH` ubicación y código. **Horarios** MUST permitir uno o más días (checkboxes) para la misma franja, lista con **Modificar** y **Eliminar**, y `PUT /api/v1/consulting-rooms/{room_id}/hours` replace atómico (`start_time < end_time`, weekday 0–6). Endpoints unitarios de hours MAY permanecer.

El menú MUST NOT mostrar **Horarios consultorio**; la ruta `/horarios-consultorio` MUST NOT existir. La gestión de franjas MUST ser el modal Horarios en `/consultorios`.

#### Scenario: Carga inicial

- **Given** usuario `operador` con consultorios en DB
- **When** abre `/consultorios`
- **Then** ve la grilla con ubicación y nombre (`code`)

#### Scenario: Menú sin Horarios consultorio

- **Given** usuario `operador`
- **When** abre el menú Distribución
- **Then** NO ve **Horarios consultorio** y sí ve **Consultorios**

#### Scenario: Reemplazar franjas

- **Given** room con una franja lunes 08–12
- **When** en modal se elimina esa y se agrega martes 09–13 y Acepta
- **Then** GET hours del room solo tiene martes 09–13

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

### Requirement: Menú Indicadores ocupación

El sistema MUST mostrar **Indicadores ocupación** → `/indicadores-ocupacion` (`admin`/`operador`). MUST coexistir con **Estadística**; MUST NOT alterar el cálculo de Estadística.

### Requirement: API e UI Indicadores ocupación (sync)

`GET /api/v1/distribucion/ocupacion/indicadores` (JWT admin|operador) MUST aceptar `period=day|month`:
- **day:** `date=YYYY-MM-DD` (cálculo de un día).
- **month:** `month=YYYY-MM`; `enabled_hours` y `occupied_hours` MUST ser la **suma** de todos los días del mes calendario (no promedio de %).

Por el período y filtros:
- **Rooms:** activos, filtros opcionales `location_id` / `room_id`.
- **Denominador (`enabled_hours`):** suma `room_operating_hours` por weekday(s) del período (JS). Rooms sin franja → `rooms_without_hours` (fuera de torta).
- **Numerador (`occupied_hours`):** duración de bloques sync con `id_agenda` mapeada a room incluido en torta; sin recorte al horario del box; filtros `especialidad`/`medico` **payload-only** solo al numerador. Sin mapeo → no cuenta. % MAY > 100.
- **Tops:** `top_especialidad` y `top_medico` (hasta 10, horas > 0, orden horas desc). Cada ítem: label, hours, `percent_box` (= ÷ enabled), `percent_occupied` (= ÷ occupied). Labels vacíos → “Sin especialidad” / “Sin médico”. Misma fuente payload que filtros. Solo bloques que entran al numerador.

UI `/indicadores-ocupacion`: control Día|Mes, selects ubicación/consultorio/especialidad/médico, KPIs, torta (horas y % por segmento; preferible donut con % al centro), tops al costado; avisos rooms sin horario / sin agenda; solo lectura; sin sync.

#### Scenario: Room sin agenda

- **Given** room con horario y sin `id_agenda`
- **When** indicadores del período
- **Then** aporta al denom y 0 al numerador

#### Scenario: Mes suma

- **Given** rooms con horario L–V y sync mapeado en varios días de un mes
- **When** period=month ese mes
- **Then** `enabled_hours` y `occupied_hours` son la suma de todos los días del mes

#### Scenario: Top solo mapeadas

- **Given** filas sync sin mapeo a consultorio y otras mapeadas
- **When** tops
- **Then** solo las mapeadas (que entran a la torta) aportan horas a los tops

### Requirement: Menú Estadística

El sistema MUST mostrar **Estadística** → `/estadisticas` (`admin`/`operador`), coexistiendo con Indicadores ocupación.

### Requirement: API e UI Estadística (asignaciones semanales)

`GET /api/v1/stats/summary` MUST aceptar rango `start_date`/`end_date` y filtros (ubicaciones, rooms, profesionales, especialidades).

- **Denominador:** horas `room_operating_hours` en el rango para rooms incluidos.
- **Numerador:** horas de `room_weekly_assignments` proyectadas por ocurrencias de weekday en el rango (NO bookings puntuales; NO sync externo). Especialidad MUST filtrar numerador sin reducir denominador.

UI `/estadisticas`: rango + filtros + torta/KPIs/series.

#### Scenario: Distinto de Indicadores

- **Given** mismo día y mismos rooms
- **When** se consulta Estadística vs Indicadores ocupación
- **Then** las fuentes de numerador son independientes (weekly assignments vs sync mapeado)
