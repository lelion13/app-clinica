# Distribución Specification

## Purpose

Dominio de distribución de consultorios: sync de ocupación (horarios activos), materialización de agenda ocupación, mapeo `(id_agenda, weekday)` → consultorio, vínculo ubicación↔ocupación `(id_dominio, tipo)`, UI de grillas e indicadores de ocupación.

## Traceability (source of truth vs archives)

| Capacidad | Spec estable (esta) | Archive origen |
|-----------|---------------------|----------------|
| Sync Ocupación `/ocupacion`, env, tabla, split `nombre_agenda`, filtros/indicadores grilla sync | § Sync y Ocupación | `2026-08-06-distribucion-ocupacion` |
| API `agenda/events` + `filter-options` (materialización) | § Agenda API | `2026-08-06-agenda-ocupacion-sync` |
| Mapeo `(id_agenda, weekday)`→room + columnas / Sin consultorio | § Mapeo | `2026-08-06-mapeo-agenda-consultorio` + `2026-10-03-consultorios-ui` + `2026-10-19-agenda-ocupacion-segun-dia` |
| `locations.tipo` + unique par + filtro location dominio+tipo | § Ubicaciones | `2026-08-06-locations-tipo` |
| UI Agenda ocupación (planilla, filtros, modal, DnD por día) | § UI Agenda | `2026-08-06-agenda-ocupacion-ui` + `2026-10-05-agenda-ocupacion-dnd` + `2026-10-19-agenda-ocupacion-segun-dia` |
| UI Consultorios (grilla, modales, horarios, Agendas por día) | § UI Consultorios | `2026-10-03-consultorios-ui` + `2026-10-19-agenda-ocupacion-segun-dia` |
| Indicadores ocupación (sync, Día\|Mes, torta, tops; filtros payload; medico sync) | § Indicadores ocupación | `2026-10-03-indicadores-ocupacion` + `2026-10-05-indicadores-ocupacion-ui` |
| Retiro Ocupación semanal / Agenda bookings / Estadística | § Retiro obsoletas | `2026-10-19-limpiar-ui-obsoleta` (rev `0033_drop_bookings_weekly`) |

**Regla anti-ambigüedad:** si un archive antiguo habla de Ocupación semanal, Agenda `/agenda` (bookings), Estadística `/estadisticas`, FullCalendar o PK=`id_dato`, **prevalece esta spec estable**. Los deltas archivados son histórico.

---

## Requirements

### Requirement: Menú Ocupación

El sistema MUST mostrar un ítem **Ocupación** bajo Distribución, path `/ocupacion`, visible para `admin` y `operador`.

El menú Distribución MUST NOT mostrar **Ocupación semanal**, **Agenda** (reservas `/agenda`) ni **Estadística**.

#### Scenario: Operador ve Ocupación sin las obsoletas

- **Given** usuario `operador`
- **When** abre el menú Distribución
- **Then** ve **Ocupación** y NO ve Ocupación semanal, Agenda ni Estadística

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

El sistema MUST persistir el mapeo **`(id_agenda, weekday)` → `room_id`** (rev `0032_agenda_map_weekday`; legado 1:1 en `0015`), donde `weekday` es 0–6 (mismo convenio JS que `room_operating_hours`). Un mismo `id_agenda` MAY tener distintos rooms por weekday. Weekdays sin fila MUST tratarse como Sin consultorio.

Migración desde 1:1: cada fila legada MUST expandirse a todos los weekdays sync parseables de ese `id_agenda` (mismo `room_id`). La migración MUST dropear la PK `id_agenda` **antes** de insertar múltiples weekdays (si no → UniqueViolation).

MUST listar/agregar/quitar desde ficha **Consultorios** (JWT admin|operador), modal Agendas draft hasta Aceptar. `PUT .../id-agendas` MUST: asignar solo weekdays aún Sin consultorio (no pisar otros rooms); todo-o-nada con validación horario/solape; listar full = una fila nombre, parcial = una fila por día `{nombre} - {día}`; unassign full = todos los días en ese room, parcial = un weekday. Endpoints unitarios POST/DELETE MAY permanecer (`DELETE` con `weekday` opcional).

MUST ofrecer lookup typeahead por médico; label `id_agenda — nombre_agenda`. `current_room_id`/`current_room_code` solo si **todos** los weekdays sync están en el mismo room activo; si no, null.

`GET .../agenda/events` MUST resolver `resource_id` con el mapa del **weekday del evento**. Indicadores MUST usar el mismo criterio por weekday.

#### Scenario: Sin mapeo ese día

- **Given** lunes mapeado a C1 y martes sin fila
- **When** events de un martes
- **Then** `resource_id` = `unassigned`

#### Scenario: Migración expand

- **Given** mapa legado Pérez→C1 y sync lunes+martes
- **When** corre `0032`
- **Then** filas (Pérez, lunes)→C1 y (Pérez, martes)→C1

#### Scenario: Lookup room completo

- **Given** agenda 100 con todos sus días sync en room `C3`
- **When** lookup
- **Then** `current_room_code=C3`

### Requirement: UI Consultorios — grilla y modales

`/consultorios` MUST, al abrir (JWT `admin`|`operador`), cargar consultorios en grilla con columnas **Ubicación** y **Nombre** (`code`), filtro select ubicación (**Todas** o una), y acciones por fila **Editar**, **Agendas**, **Horarios**, **Eliminar** (`window.confirm`).

**Agregar** MUST abrir modal ubicación + código. Modales Agregar/Editar/Agendas/Horarios MUST ser draft hasta **Aceptar**; **Cancelar** MUST NOT persistir. Solo un modal abierto a la vez.

**Editar** MUST `PATCH` ubicación y código. **Horarios** MUST permitir uno o más días (checkboxes) para la misma franja, lista con **Modificar** y **Eliminar**, y `PUT /api/v1/consulting-rooms/{room_id}/hours` replace atómico (`start_time < end_time`, weekday 0–6). Endpoints unitarios de hours MAY permanecer.

Modal **Agendas** MUST seguir las reglas de mapeo por weekday (assign solo pendientes, labels full/parcial, unassign por día o full, conflicto modal todo-o-nada).

El menú MUST NOT mostrar **Horarios consultorio**; la ruta `/horarios-consultorio` MUST NOT existir. La gestión de franjas MUST ser el modal Horarios en `/consultorios`.

#### Scenario: Carga inicial

- **Given** usuario `operador` con consultorios en DB
- **When** abre `/consultorios`
- **Then** ve la grilla con ubicación y nombre (`code`)

#### Scenario: Menú sin Horarios consultorio

- **Given** usuario `operador`
- **When** abre el menú Distribución
- **Then** NO ve **Horarios consultorio** y sí ve **Consultorios**

#### Scenario: Assign no pisa otro room

- **Given** lunes en C2; martes Sin consultorio
- **When** assign a C1 desde Consultorios
- **Then** solo el martes pasa a C1; el lunes permanece en C2

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

Menú **Agenda ocupación** `/agenda-ocupacion` (`admin`/`operador`). MUST NOT sync (sync solo en Ocupación). Las rutas legacy `/agenda`, `/ocupacion-semanal` y `/estadisticas` MUST redirigir a Home.

MUST mostrar grilla día × consultorios (+ **Sin consultorio**), horas alineadas, full-bleed + altura viewport, scroll interno, cabecera sticky, columnas ≥160px.

Columnas de consultorios MUST ordenarse por número en `code` (C1…C10); códigos sin número al final. Si no caben: scroll horizontal; durante drag cerca del borde, auto-scroll H. **Sin consultorio** MUST ser sticky a la izquierda si tiene ítems; si vacía, scroll con el resto.

Filtros en **una fila** de selects: Ubicación, Día (+ nav), Tipo, Especialidad, Médico. Solo agendas con bloque sync el weekday del calendario.

Click bloque → modal; Esc / overlay / Cerrar. DnD horizontal (ver Reassign); MUST NOT drag vertical / resize de horas sync.

#### Scenario: Filtros en una fila

- **Given** desktop
- **When** abre Agenda ocupación
- **Then** filtros en una banda compacta

#### Scenario: Cierre modal

- **Given** modal abierto
- **When** Esc o overlay
- **Then** se cierra

#### Scenario: DnD con filtros

- **Given** filtro de ubicación que oculta room X
- **When** el usuario arrastra un bloque
- **Then** no puede soltar en X (no visible)

### Requirement: Reassign agenda via Agenda ocupación (DnD)

El sistema MUST reasignar **solo el weekday del día del calendario** vía DnD. `POST /api/v1/distribucion/ocupacion/agenda/reassign` (JWT `admin`|`operador`) MUST incluir `weekday`. Otras filas `(id_agenda, otros weekdays)` MUST permanecer intactas. Solo columnas visibles son destinos.

#### Scenario: Asignar solo el lunes

- **Given** agenda lunes+martes Sin consultorio; calendario lunes; C1 válido
- **When** drop en C1
- **Then** solo lunes en C1; martes sigue Sin consultorio

#### Scenario: Desasignar solo el día

- **Given** lunes y martes en C1; calendario lunes
- **When** drop a Sin consultorio
- **Then** se borra solo el mapa del lunes

### Requirement: Validación horario box y sin solape (path reassign)

Al asignar/mover en AO, el backend MUST validar **únicamente el weekday reasignado**: cobertura `room_operating_hours` y sin solape ese weekday (half-open; excluir `(id_agenda, weekday)`). Fallo → no persistir + error detallado.

El path Consultorios Agendas MUST aplicar la misma validación al asignar días pendientes (todo-o-nada).

#### Scenario: Martes conflictivo no bloquea lunes

- **Given** lunes OK en C1 y solape el martes en C1
- **When** reassign del lunes a C1
- **Then** el lunes se acepta

### Requirement: Confirmaciones robo y desasignar

Robo: si `(id_agenda, weekday)` está en otro room → UI confirm + `confirm_move`; sin confirm → 409. Desasignar en AO: UI confirm + `confirm_unassign`; sin validar horario/solape; solo ese weekday.

### Requirement: Feedback de rechazo DnD

Fallo de validación → modal con motivo detallado; bloque permanece en columna origen.

### Requirement: Menú Indicadores ocupación

El sistema MUST mostrar **Indicadores ocupación** → `/indicadores-ocupacion` (`admin`/`operador`). MUST NOT depender de Estadística ni de `weekly-assignments` / `/stats`.

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

### Requirement: Retiro de Ocupación semanal, Agenda bookings y Estadística

El sistema MUST NOT exponer UI ni API de Ocupación semanal (`/ocupacion-semanal`, `/api/v1/weekly-assignments`), Agenda reservas (`/agenda`, `/api/v1/bookings`) ni Estadística (`/estadisticas`, `/api/v1/stats`).

Las rutas FE legacy MUST redirigir a `/`. Las tablas exclusivas `bookings` y `room_weekly_assignments` MUST eliminarse (rev `0033_drop_bookings_weekly`). MUST NOT eliminar `professionals`, consultorios ni `room_operating_hours`.

#### Scenario: Redirect legacy

- **Given** usuario autenticado
- **When** navega a `/estadisticas` o `/agenda` o `/ocupacion-semanal`
- **Then** termina en Home

#### Scenario: API ausente

- **Given** JWT válido
- **When** GET `/api/v1/stats/summary` o `/api/v1/bookings` o `/api/v1/weekly-assignments`
- **Then** 404 (ruta no montada)
