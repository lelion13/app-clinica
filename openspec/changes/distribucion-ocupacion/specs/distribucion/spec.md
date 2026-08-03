# Delta: distribución — Ocupación (horarios activos)

## ADDED Requirements

### Requirement: Menú Ocupación

El sistema MUST mostrar un ítem **Ocupación** bajo Distribución de consultorios, con path `/ocupacion`, visible para roles `admin` y `operador`. El ítem **Ocupación semanal** MUST permanecer sin cambios.

#### Scenario: Operador ve ambos ítems

- **Given** un usuario autenticado con rol `operador`
- **When** abre el menú Distribución de consultorios
- **Then** ve **Ocupación semanal** y **Ocupación** como entradas distintas

### Requirement: Proxy JWT de horarios activos

El backend MUST exponer `GET /api/v1/distribucion/ocupacion/horarios-activos` protegido con JWT y `require_operator_or_admin`. MUST consultar la URL de `DISTRIBUCION_HORARIOS_ACTIVOS_URL` con Bearer `NOVEDADES_PROF_SYNC_TOKEN`. El token MUST NOT devolverse al cliente.

#### Scenario: Config ausente

- **Given** falta URL o token
- **When** un operador llama al endpoint
- **Then** la API responde 422 con mensaje genérico de configuración

#### Scenario: Upstream falla

- **Given** URL y token configurados y la API externa falla
- **When** un operador llama al endpoint
- **Then** la API responde 502 sin incluir el token en el detalle

#### Scenario: Respuesta OK

- **Given** la API externa responde una lista de objetos
- **When** un operador llama al endpoint
- **Then** recibe `items` con al menos: `id_dominio`, `tipo`, `especialidad_agenda`, `medico`, `especialidad`, `dia`, `fecha_desde`, `hora_desde`, `fecha_hasta`, `hora_hasta`, `duracion_turno`
- **And** solo incluye filas con `fecha_hasta` parseable y `fecha_hasta >= hoy` (`BUSINESS_TIMEZONE`); sin fecha o inválida se excluyen

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

Debe existir un botón **Indicadores** que abre un modal con resumen de las filas visibles. Agrupación: `id_dominio` + `especialidad` + `medico` + `dia`. Por fila válida: horas = (`hora_hasta` − `hora_desde`) en horas; `cantidad_turnos` = (diferencia en minutos) / `duracion_turno`. Filas con horas inválidas o `duracion_turno` ≤ 0 MUST excluirse del cálculo. Las métricas del grupo MUST ser la suma de las filas del grupo.

#### Scenario: Indicadores tras filtrar

- **Given** el usuario filtró la grilla
- **When** pulsa Indicadores
- **Then** el modal muestra grupos solo a partir de las filas filtradas, con columnas id_dominio, especialidad, medico, dia, horas, cantidad_turnos
