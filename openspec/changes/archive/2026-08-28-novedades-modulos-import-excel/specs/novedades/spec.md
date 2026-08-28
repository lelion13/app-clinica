# Delta for novedades

## ADDED Requirements

### Requirement: Plantilla Excel import módulos

Parametrización tab **Módulos** MUST offer **Plantilla de importación** for `admin`/`rrhh`. Download MUST be an `.xlsx` with headers for module fields and a **dropdown of existing active service names** on the service column. Producción and SADOFE MUST use Sí/No dropdowns.

#### Scenario: Descargar plantilla

- GIVEN admin en tab Módulos con servicios activos S1, S2
- WHEN pulsa Plantilla de importación
- THEN descarga un Excel con columnas de módulo
- AND la columna servicio ofrece S1 y S2 en lista desplegable

### Requirement: Carga masiva módulos

Parametrización tab **Módulos** MUST offer **Carga masiva** for `admin`/`rrhh` to upload the filled template. Each data row MUST map to at most one service. Empty `valor` MUST become 0. Comentario MAY be empty. Descripción and servicio MUST be required.

Import MUST be **all-or-nothing**: if any row is invalid, MUST NOT create any module. Duplicate active module description MUST be an error. Unknown/inactive service name MUST be an error. Invalid Sí/No or non-numeric valor MUST be an error.

On failure, the UI MUST show a modal listing each failing row and reason. On success, modules MUST appear in the list and the UI MUST confirm how many were created.

#### Scenario: Import OK

- GIVEN Excel con filas válidas y servicios existentes
- WHEN admin ejecuta Carga masiva
- THEN se crean todos los módulos asociados a su servicio
- AND la lista de módulos se actualiza

#### Scenario: Error todo o nada

- GIVEN Excel con 3 filas válidas y 1 con descripción duplicada
- WHEN admin ejecuta Carga masiva
- THEN no se crea ningún módulo
- AND un modal lista la fila inválida y el motivo

#### Scenario: Servicio inexistente

- GIVEN fila con servicio no activo / no existente
- WHEN importa
- THEN MUST fallar esa fila con motivo claro
- AND MUST NOT persistir ninguna fila del archivo
