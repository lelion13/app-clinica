# Delta for distribucion — locations.tipo

## ADDED Requirements

### Requirement: Ubicación vinculada por id_dominio + tipo

El sistema MUST persistir `locations.tipo` (string no vacío) y MUST exigir `tipo` en create y update.

Entre ubicaciones activas (`deleted_at IS NULL`), el par `(id_dominio, tipo)` MUST ser único.

Al filtrar Agenda ocupación por `location_id`, el sistema MUST restringir eventos al `id_dominio` y al `tipo` de esa ubicación (comparación case-insensitive trim).

El label de ubicación en eventos SHOULD resolverse por `(id_dominio, tipo)`; si no hay match exacto, MAY hacer fallback al primer nombre con ese `id_dominio` o al número.

#### Scenario: Mismo dominio, distinto tipo

- **Given** dos locations activas con `id_dominio=1651` y tipos `SEDE TORRE` / `SEDE CAÑUELAS`
- **When** se filtra agenda por la location Torre
- **Then** solo aparecen eventos con tipo equivalente a `SEDE TORRE`

#### Scenario: Create sin tipo

- **Given** un POST `/locations` sin `tipo` o con `tipo` en blanco
- **When** se valida el payload
- **Then** la API rechaza la request (422)

## MODIFIED Requirements

### Requirement: Split de nombre_agenda (ampliación)

(Previously: solo separador `" - "`.)

El backend MUST intentar partir `nombre_agenda` por `" - "`. Si no hay ese separador y el valor contiene `-`, MUST partir por `-` (partes strip). Parte 1 → `tipo`, parte 2 → `especialidad_agenda`, resto → `medico`.

#### Scenario: Nombre compacto con guiones

- **Given** `nombre_agenda` = `CMG-ECOGRAFIA-DR. BARRERA`
- **When** se sincroniza / deriva columnas
- **Then** `tipo=CMG`, `especialidad_agenda=ECOGRAFIA`, `medico` contiene el resto
