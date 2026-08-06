# Delta for distribucion

## MODIFIED Requirements

### Requirement: UI Agenda ocupación

(Previously: FullCalendar + popover; filtros dominio/tipo/especialidad/médico/día en UI genérica.)

La pantalla `/agenda-ocupacion` MUST:

- Mostrar grilla día × consultorios (+ columna **Sin consultorio**) con eje de horas a la izquierda.
- Alinear visualmente cada marca de hora con el inicio de la fila correspondiente en todas las columnas (sin drift por bordes/box model).
- Usar el ancho disponible del panel de contenido y la altura restante del viewport: scroll vertical/horizontal **dentro** de la grilla; cabecera (HORA + títulos de consultorio) MUST permanecer sticky al hacer scroll.
- Usar anchos mínimos de columna más generosos que el baseline actual (`120px`); MAY hacer scroll horizontal si hay muchos consultorios.
- Exponer filtros: **Ubicación**, **Día** (navegación existente), y multi-select **tipo**, **especialidad**, **médico**.
- Obtener opciones de filtro desde `GET .../ocupacion/agenda/filter-options` (o equivalente ya existente).
- Al cambiar filtros o día, MUST volver a pedir `GET .../ocupacion/agenda/events` pasando los valores seleccionados; filtros vacíos = sin restricción en ese eje.
- Eventos en **Sin consultorio** MUST respetar los mismos filtros que el resto de columnas (ubicación + tipo + especialidad + médico + día).
- Al click en un bloque, MUST abrir un **modal centrado** con overlay semitransparente y el detalle extendido.
- El modal MUST cerrarse con: tecla Escape, clic en el overlay, o control explícito Cerrar.
- Permanecer solo lectura; MUST NOT invocar sync.

#### Scenario: Alineación hora–fila

- **Given** la grilla visible de 06:00 a 22:00
- **When** el usuario observa la marca `08:00` y la línea horizontal de las columnas
- **Then** coinciden en la misma coordenada vertical

#### Scenario: Filtro reduce Sin consultorio

- **Given** eventos unassigned de varios tipos en el día
- **When** el usuario selecciona un `tipo` en el multi-select y aplica/recarga
- **Then** la columna Sin consultorio solo muestra bloques de ese tipo (y los demás filtros activos)

#### Scenario: Cierre de modal

- **Given** el modal de detalle abierto
- **When** el usuario presiona Escape o hace clic en el overlay
- **Then** el modal se cierra

## ADDED Requirements

### Requirement: Layout viewport de Agenda ocupación

El contenedor de la grilla SHOULD ocupar el alto restante bajo título + barra de filtros (`flex` o `calc` sobre viewport), de modo que la página no dependa solo del scroll del documento para navegar horas.

#### Scenario: Scroll interno

- **Given** viewport de altura típica de laptop
- **When** el usuario desplaza la grilla verticalmente
- **Then** título/filtros permanecen visibles y la cabecera de columnas permanece sticky dentro del área de grilla
