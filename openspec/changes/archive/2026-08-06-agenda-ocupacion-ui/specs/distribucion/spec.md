# Delta for distribucion — agenda-ocupacion-ui

## MODIFIED Requirements

### Requirement: UI Agenda ocupación

(Previously: FullCalendar + popover; luego grilla + listas multi-select altas.)

La pantalla `/agenda-ocupacion` MUST:

- Mostrar grilla día × consultorios (+ **Sin consultorio**) con eje de horas a la izquierda.
- Alinear cada marca de hora con el inicio de la fila en todas las columnas (sin drift por box model).
- Usar ancho full-bleed del viewport y la altura restante: scroll **dentro** de la grilla; cabecera HORA + consultorios sticky.
- Columnas con ancho mínimo generoso (≥160px); MAY scroll horizontal.
- Exponer filtros en **una sola fila horizontal** (MAY scroll-x en viewports angostos): **Ubicación**, **Día** (+ nav Hoy/←/→), **Tipo**, **Especialidad**, **Médico**.
- Cada filtro de catálogo MUST ser un **select de un valor** con opción vacía = sin restricción (mismo patrón que Ubicación), alimentado por `GET .../ocupacion/agenda/filter-options` donde aplique.
- Al cambiar filtros o día, MUST pedir de nuevo `GET .../ocupacion/agenda/events` con los valores elegidos.
- Eventos en **Sin consultorio** MUST respetar los mismos filtros que el resto.
- Click en bloque → **modal centrado** con overlay; cierre Escape, clic overlay, o Cerrar.
- Solo lectura; MUST NOT invocar sync.
- El chrome de título/ayuda SHOULD ser mínimo para maximizar la grilla.

#### Scenario: Alineación hora–fila

- **Given** la grilla 06:00–22:00
- **When** se observa la marca `08:00` y la línea de columnas
- **Then** coinciden en la misma coordenada vertical

#### Scenario: Filtros en una fila

- **Given** viewport desktop típico
- **When** se carga Agenda ocupación
- **Then** Ubicación, Día, Tipo, Especialidad y Médico están visibles en una sola banda horizontal compacta (sin listas checkbox altas)

#### Scenario: Filtro reduce Sin consultorio

- **Given** eventos unassigned de varios tipos
- **When** el usuario elige un `tipo` en el select
- **Then** Sin consultorio solo muestra bloques de ese tipo (más demás filtros activos)

#### Scenario: Cierre de modal

- **Given** modal abierto
- **When** Escape o clic en overlay
- **Then** el modal se cierra

## ADDED Requirements

### Requirement: Layout viewport de Agenda ocupación

El contenedor de la grilla SHOULD ocupar el alto restante bajo título + barra de filtros, de modo que la grilla sea el elemento visual dominante para detectar huecos libres.

#### Scenario: Scroll interno

- **Given** laptop típica
- **When** el usuario scrollea la grilla
- **Then** la banda de filtros permanece usable y la cabecera de columnas sticky dentro del área de grilla
