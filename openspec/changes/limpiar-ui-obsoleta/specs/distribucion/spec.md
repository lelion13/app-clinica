# Delta Spec: distribucion — limpiar-ui-obsoleta

## REMOVED Requirements

### Requirement: Menú Estadística

(Removed: ítem Estadística y ruta `/estadisticas`.)

### Requirement: API e UI Estadística (asignaciones semanales)

(Removed: `GET /api/v1/stats/summary` y UI `/estadisticas`.)

## MODIFIED Requirements

### Requirement: Menú Ocupación

(Previously: Ocupación semanal MUST permanecer como ítem distinto.)

El sistema MUST mostrar un ítem **Ocupación** bajo Distribución, path `/ocupacion`, visible para `admin` y `operador`.

El menú Distribución MUST NOT mostrar **Ocupación semanal**, **Agenda** (reservas `/agenda`) ni **Estadística**.

#### Scenario: Operador ve Ocupación sin las obsoletas

- **Given** usuario `operador`
- **When** abre el menú Distribución
- **Then** ve **Ocupación** y NO ve Ocupación semanal, Agenda ni Estadística

### Requirement: UI Agenda ocupación

(Previously: decía “`/agenda` (bookings) intacta”.)

Menú **Agenda ocupación** `/agenda-ocupacion` (`admin`/`operador`). MUST NOT sync (sync solo en Ocupación).

La ruta legacy `/agenda` MUST redirigir a Home. MUST NOT existir pantalla de bookings.

(Resto de requisitos de grilla/DnD/orden/scroll de la spec estable se mantienen.)

### Requirement: Menú Indicadores ocupación

(Previously: coexistir con Estadística.)

El sistema MUST mostrar **Indicadores ocupación** → `/indicadores-ocupacion` (`admin`/`operador`). MUST NOT depender de Estadística ni de `weekly-assignments` / `/stats`.

## ADDED Requirements

### Requirement: Retiro de Ocupación semanal y Agenda bookings

El sistema MUST NOT exponer UI ni API de:

- Ocupación semanal (`/ocupacion-semanal`, `/api/v1/weekly-assignments`)
- Agenda reservas (`/agenda`, `/api/v1/bookings`)
- Estadística (`/estadisticas`, `/api/v1/stats`)

Las rutas FE legacy MUST redirigir a `/` (Home).

Tras verificación de no-uso cruzado, MUST eliminarse el código y las tablas exclusivas (`bookings`, `room_weekly_assignments`). MUST NOT eliminar `professionals`, consultorios ni horarios de box.

#### Scenario: Redirect legacy

- **Given** usuario autenticado
- **When** navega a `/estadisticas` o `/agenda` o `/ocupacion-semanal`
- **Then** termina en Home

#### Scenario: API ausente

- **Given** JWT válido
- **When** GET `/api/v1/stats/summary` o `/api/v1/bookings` o `/api/v1/weekly-assignments`
- **Then** 404 (ruta no montada)
