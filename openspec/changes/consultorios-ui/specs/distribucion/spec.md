# Delta Spec: distribucion — consultorios-ui

## ADDED Requirements

### Requirement: UI Consultorios — grilla y filtro

`/consultorios` MUST, al abrir (JWT `admin`|`operador`), cargar la lista de consultorios existentes.

La grilla MUST mostrar columnas **Ubicación** (nombre de location) y **Nombre** (valor de `code`). Cada fila MUST ofrecer acciones **Editar**, **Agendas**, **Horarios** y **Eliminar**.

Arriba de la grilla MUST haber un filtro select de ubicación con opción **Todas** y una ubicación a la vez. Con **Todas**, MUST listar todos los consultorios; con una ubicación, MUST listar solo los de esa `location_id`.

**Eliminar** MUST pedir confirmación simple (`window.confirm` o equivalente) antes del DELETE. Tras eliminar OK, MUST refrescar la grilla.

**Agregar** MUST abrir un modal (no form inline) pidiendo ubicación y código, con **Aceptar** / **Cancelar**.

#### Scenario: Carga inicial

- **Given** usuario `operador` con consultorios en DB
- **When** abre `/consultorios`
- **Then** ve la grilla con ubicación y nombre (`code`) sin seleccionar nada previo

#### Scenario: Filtro ubicación

- **Given** consultorios en dos ubicaciones
- **When** elige una ubicación en el filtro
- **Then** solo se listan consultorios de esa ubicación

#### Scenario: Eliminar con confirm

- **Given** un consultorio en grilla
- **When** pulsa Eliminar y confirma
- **Then** el consultorio desaparece de la grilla
- **And** si cancela el confirm, MUST NOT eliminarse

### Requirement: Modales draft Aceptar / Cancelar

Los modales **Agregar**, **Editar**, **Agendas** y **Horarios** MUST trabajar en draft local hasta **Aceptar**.

- **Aceptar** MUST persistir los cambios del modal y cerrar.
- **Cancelar** (o cerrar sin aceptar) MUST descartar el draft y MUST NOT persistir cambios de ese modal.

Solo un modal de estos MUST estar abierto a la vez (abrir otro implica cerrar/descartar el actual, o bloquear hasta cerrar — implementación SHOULD cerrar/descartar el abierto).

#### Scenario: Cancelar Editar

- **Given** modal Editar con código modificado en draft
- **When** pulsa Cancelar
- **Then** el modal cierra y la grilla muestra el código original

### Requirement: Modal Editar consultorio

**Editar** MUST abrir modal con ubicación y código del consultorio. **Aceptar** MUST llamar `PATCH /consulting-rooms/{id}` con esos campos. Validación MUST rechazar código vacío.

#### Scenario: Editar ubicación y código

- **Given** consultorio con código `A1`
- **When** edita a otra ubicación y código `B2` y Acepta
- **Then** la grilla refleja ubicación y nombre `B2`

### Requirement: Modal Agregar consultorio

**Agregar** MUST pedir ubicación y código. **Aceptar** MUST `POST /consulting-rooms` y refrescar la grilla. Cancelar MUST NOT crear.

#### Scenario: Agregar OK

- **Given** ubicación válida y código no vacío
- **When** Acepta en modal Agregar
- **Then** el nuevo consultorio aparece en la grilla

### Requirement: Modal Agendas (draft + batch)

**Agendas** MUST abrir modal para el consultorio de la fila con:
- typeahead de agendas (mismo lookup que hoy)
- lista draft de agendas asociadas
- quitar del draft

Al elegir una agenda en typeahead, el sistema MUST usar datos de solo lectura del lookup (campos `current_room_id` / `current_room_code` cuando existan). Si ya está mapeada a **otro** consultorio, MUST pedir confirmación de mover; si el usuario acepta, el ítem entra al draft con `confirm_move=true`; si rechaza, MUST NOT agregarse al draft. Si ya está en **este** consultorio, MUST NOT duplicar.

**Aceptar** MUST persistir con `PUT /api/v1/consulting-rooms/{room_id}/id-agendas` enviando la lista desired completa (cada ítem con `id_agenda` y `confirm_move`). El backend MUST aplicar el replace en una transacción (todo-o-nada). Si algún ítem requiere move y `confirm_move` es false, MUST responder 409 sin aplicar el batch.

Endpoints unitarios POST/DELETE de id-agendas MAY permanecer; la UI de este change MUST usar el PUT batch en Aceptar.

#### Scenario: Asociar con confirm en draft

- **Given** `id_agenda` 100 mapeado al consultorio X
- **When** en modal Agendas de consultorio Y se elige 100 y se confirma mover
- **And** Acepta
- **Then** 100 queda solo en Y

#### Scenario: Cancelar no persiste agendas

- **Given** draft con agendas nuevas
- **When** Cancelar
- **Then** GET agendas del room permanece igual que antes de abrir el modal

### Requirement: Modal Horarios (draft + batch)

**Horarios** MUST abrir modal con la UX de franjas actual: día (0=domingo…6=sábado), desde, hasta, agregar franja al draft, lista con eliminar del draft. MUST precargar franjas existentes del room.

**Aceptar** MUST `PUT /api/v1/consulting-rooms/{room_id}/hours` con la lista desired de franjas (`weekday`, `start_time`, `end_time`). El backend MUST replace atómico en transacción (eliminar las no listadas / crear las nuevas según implementación, resultado final = lista desired). Validación MUST exigir `start_time < end_time` y weekday 0–6.

Endpoints unitarios de hours MAY permanecer; la UI MUST usar PUT batch en Aceptar.

#### Scenario: Reemplazar franjas

- **Given** room con una franja lunes 08–12
- **When** en modal se elimina esa y se agrega martes 09–13 y Acepta
- **Then** GET hours del room solo tiene martes 09–13

### Requirement: Agenda lookup con mapeo actual

`GET /api/v1/distribucion/ocupacion/agenda-lookup` MUST, por cada ítem, incluir cuando el `id_agenda` esté mapeado a un consultorio no borrado:
- `current_room_id` (int)
- `current_room_code` (string)

Si no está mapeado, esos campos MUST ser null u omitirse de forma consistente (null). Auth sin cambio (`admin`|`operador`).

#### Scenario: Lookup muestra room actual

- **Given** agenda 100 asociada al room código `C3`
- **When** lookup encuentra esa agenda
- **Then** el ítem incluye `current_room_id` y `current_room_code=C3`

## REMOVED Requirements

### Requirement: Pantalla y menú Horarios consultorio

El sistema MUST NOT mostrar el ítem de menú **Horarios consultorio** bajo Distribución.

La ruta `/horarios-consultorio` MUST NOT existir (404 / no match). La gestión de franjas MUST hacerse desde el modal **Horarios** en `/consultorios`.

#### Scenario: Menú sin Horarios

- **Given** usuario `operador`
- **When** abre el menú Distribución
- **Then** NO ve **Horarios consultorio**
- **And** sí ve **Consultorios**

#### Scenario: Ruta eliminada

- **Given** usuario autenticado
- **When** navega a `/horarios-consultorio`
- **Then** no se renderiza la pantalla de horarios (404 o redirect de router sin esa route)
