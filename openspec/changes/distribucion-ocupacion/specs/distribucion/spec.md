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
- **Then** recibe `items` con al menos: `id_dominio`, `especialidad`, `fecha_desde`, `hora_desde`, `fecha_hasta`, `hora_hasta`, `duracion_turno`

### Requirement: Grilla Ocupación (v1)

La pantalla `/ocupacion` MUST cargar automáticamente al abrir, MUST ofrecer **Actualizar**, y MUST mostrar una grilla con las columnas v1 anteriores.

#### Scenario: Carga al abrir

- **Given** un admin autenticado
- **When** navega a `/ocupacion`
- **Then** se solicita el proxy y se renderiza la grilla (o un error visible si falla)
