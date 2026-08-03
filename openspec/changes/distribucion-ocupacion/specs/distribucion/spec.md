# Delta: distribución — Ocupación (horarios activos)

## ADDED Requirements

### Requirement: Menú Ocupación

El sistema MUST mostrar un ítem **Ocupación** bajo Distribución de consultorios, con path `/ocupacion`, visible para roles `admin` y `operador`. El ítem **Ocupación semanal** MUST permanecer sin cambios.

#### Scenario: Operador ve ambos ítems

- **Given** un usuario autenticado con rol `operador`
- **When** abre el menú Distribución de consultorios
- **Then** ve **Ocupación semanal** y **Ocupación** como entradas distintas

### Requirement: Persistencia y sync de horarios activos

El backend MUST persistir el snapshot completo del endpoint externo en `ocupacion_horario_activo` (PK `id_dato`, incluyendo columnas derivadas `tipo`/`especialidad_agenda`/`medico`). `POST /api/v1/distribucion/ocupacion/horarios-activos/sync` MUST, tras GET externo OK, borrar y recargar la tabla en una sola transacción. Si el GET falla, MUST NOT modificar la tabla. `GET /api/v1/distribucion/ocupacion/horarios-activos` MUST leer de DB y filtrar `fecha_hasta >= hoy`. Ambos endpoints MUST exigir JWT + `admin`/`operador`. El token MUST NOT devolverse al cliente.

#### Scenario: Sync OK

- **Given** URL/token configurados y la API externa responde OK
- **When** un operador hace POST sync
- **Then** la tabla queda con exactamente las filas del payload (por `id_dato`) y la respuesta incluye `synced`

#### Scenario: Sync con upstream fallido

- **Given** datos previos en DB y la API externa falla
- **When** un operador hace POST sync
- **Then** responde 502 y los datos previos permanecen

#### Scenario: Listado vigente

- **Given** filas persistidas con `fecha_hasta` pasada y futura
- **When** un operador hace GET list
- **Then** solo recibe filas con `fecha_hasta >= hoy`

### Requirement: Split de `nombre_agenda`

El backend MUST derivar `tipo`, `especialidad_agenda` y `medico` partiendo `nombre_agenda` por el separador ` - `. Parte 1 → `tipo`, parte 2 → `especialidad_agenda`, resto unido → `medico`. Partes faltantes MUST ser null. La grilla MUST NOT mostrar `nombre_agenda` crudo.

#### Scenario: Tres partes

- **Given** `nombre_agenda` = `ART - TRAUMATOLOGIA - APECECHEA CAIRONE DIEGO`
- **When** se mapea la fila
- **Then** `tipo`=`ART`, `especialidad_agenda`=`TRAUMATOLOGIA`, `medico`=`APECECHEA CAIRONE DIEGO`

### Requirement: Grilla Ocupación (v1)

La pantalla `/ocupacion` MUST cargar automáticamente al abrir, MUST ofrecer **Actualizar**, y MUST mostrar una grilla en este orden: `id_dominio`, `tipo`, `especialidad_agenda`, `medico`, `especialidad`, `dia`, `fecha_desde`, `hora_desde`, `fecha_hasta`, `hora_hasta`, `duracion_turno`.

#### Scenario: Carga al abrir

- **Given** un admin autenticado
- **When** navega a `/ocupacion`
- **Then** se solicita el proxy y se renderiza la grilla (o un error visible si falla)

### Requirement: Filtros por columna

La grilla MUST permitir filtrar por **todas** las columnas con multi-select de valores distintos (OR dentro de columna, AND entre columnas). Select vacío = sin filtro en esa columna.

#### Scenario: Filtro por id_dominio

- **Given** filas con varios `id_dominio`
- **When** el usuario selecciona uno o más valores en el filtro `id_dominio`
- **Then** la grilla solo muestra filas cuyo `id_dominio` está entre los seleccionados

### Requirement: Indicadores sobre lo filtrado

Debe existir un botón **Indicadores** que abre un modal con resumen de las filas visibles. Agrupación: `id_dominio` + `especialidad` + `medico` + `dia`. Filas sin `dia` o con horas inválidas MUST excluirse. Por fila válida: `horas` = (`hora_hasta` − `hora_desde`); `cantidad_turnos` y `cantidad_sobreturno` MUST tomarse de la API y sumarse (incluidas repeticiones del mismo `id_agenda` en el mismo `dia`). El modal MUST mostrar esas tres métricas sumadas por grupo.

#### Scenario: Indicadores tras filtrar

- **Given** el usuario filtró la grilla
- **When** pulsa Indicadores
- **Then** el modal muestra grupos solo a partir de las filas filtradas, con columnas id_dominio, especialidad, medico, dia, horas, cantidad_turnos, cantidad_sobreturno
