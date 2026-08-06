# Delta for distribucion

## ADDED Requirements

### Requirement: Agenda ocupación — eventos de calendario

El sistema MUST exponer `GET /api/v1/distribucion/ocupacion/agenda/events` protegido con JWT y roles `admin` u `operador`.

El endpoint MUST exigir query `start` y `end` (ISO date o datetime) definiendo la ventana visible `[start, end)`.

El sistema MUST materializar un evento por cada ocurrencia de fila sync cuyo:

- `dia` sea un día de semana válido (español normalizado), AND
- el rango `[fecha_desde, fecha_hasta]` de la fila se solape con la ventana, AND
- exista al menos un día calendario en la ventana que coincida con `dia` y caiga dentro de `[fecha_desde, fecha_hasta]`.

Cada evento MUST incluir: `start`, `end` (datetime locales negocio), `title` (= `medico` o string vacío), e `extended` con campos de detalle (id_dominio, tipo, especialidades, medico, dia, fechas/horas, duracion_turno, cantidades, location_name).

Filas sin `dia` válido o sin horas parseables MUST NOT generar eventos.

#### Scenario: Ventana semanal con lunes vigente

- **Given** una fila con `dia=lunes`, `hora_desde=09:00`, `hora_hasta=12:00`, fechas que cubren ese lunes
- **When** se pide events para una semana que incluye ese lunes
- **Then** la respuesta incluye un evento ese lunes 09:00–12:00

#### Scenario: Fuera de rango de vigencia de la fila

- **Given** una fila con `fecha_hasta` anterior al `start` de la ventana
- **When** se listan events
- **Then** esa fila no genera eventos

### Requirement: Filtros de agenda ocupación

El endpoint MUST aceptar filtros opcionales (multi-valor o CSV/repetidos según implementación): `id_dominio`, `tipo`, `especialidad`, `medico`, `dia`.

- `especialidad` MUST matchear si el valor iguala `especialidad` **o** `especialidad_agenda` (case-insensitive trim).
- Filtros vacíos MUST significar sin restricción en ese eje.
- El label de dominio en opciones/detalle MUST usar `locations.name` cuando exista `id_dominio` activo; si no hay match, MUST usar el número como string.

#### Scenario: Filtro especialidad OR

- **Given** fila con especialidad API distinta de especialidad_agenda
- **When** se filtra por el valor de especialidad_agenda
- **Then** la fila sigue generando eventos

### Requirement: UI Agenda ocupación

*(SUPERSEDED 2026-08 — histórico de este change.)*

La app MUST ofrecer menú **Agenda ocupación** en `/agenda-ocupacion` para `admin`/`operador`, solo lectura, sin sync.

**UI vigente** (no FullCalendar/popover de este delta): archives `mapeo-agenda-consultorio` + `agenda-ocupacion-ui` y `openspec/specs/distribucion/spec.md` § UI Agenda ocupación.

**API** `agenda/events` + `filter-options` de este change **sigue vigente**.
