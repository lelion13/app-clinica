# Delta Spec: novedades-modulos-filtro-ui

## MODIFIED Requirements

### Requirement: Servicios y módulos

The system MUST provide ABM of **servicios** and **módulos** in Parametrización.

In tab **Módulos**, the toolbar MUST include a real-time text filter input located between the **"Nuevo módulo"** button and the **"Plantilla de importación"** button.

The filter MUST:
1. Filter the displayed modules in real-time as the user types without requiring form submission or server roundtrips.
2. Be case-insensitive and accent-insensitive (diacritics agnostic, e.g. "pediatrico" matches "Pediátrico").
3. Match against:
   - Module description (`descripcion`).
   - Module comment (`comentario`).
   - Any associated service name (`servicio_nombres`).
4. When a filter string matches an associated service name, all modules associated to that service MUST remain visible.
5. If no modules match the current filter, the list MUST display an empty state message ("No se encontraron módulos que coincidan con la búsqueda.").

#### Scenario: Filtrar por nombre de módulo
- GIVEN el usuario en la pestaña Módulos con módulos "Guardia 24hs" y "Consulta Externa"
- WHEN escribe "guardia" en el filtro
- THEN la lista muestra únicamente "Guardia 24hs"

#### Scenario: Filtrar por servicio asociado
- GIVEN un módulo "Módulo Estándar" asociado al servicio "Tocoginecología"
- AND otro módulo "Módulo UTI" asociado solo a "UTIA"
- WHEN el usuario escribe "toco" o "tocoginecologia" en el filtro
- THEN la lista muestra "Módulo Estándar" y oculta "Módulo UTI"

#### Scenario: Sin coincidencias
- GIVEN una lista de módulos activos
- WHEN el usuario ingresa un término que no coincide con ninguna descripción, comentario ni servicio
- THEN la lista muestra el mensaje de búsqueda sin resultados
