# Proposal: novedades-modulos-filtro-ui

## Intent

Agregar un campo de búsqueda/filtro en tiempo real dentro de la pestaña **Módulos** de Parametrización, ubicado entre el botón **"Nuevo módulo"** y el botón **"Plantilla de importación"**, permitiendo filtrar la lista de módulos por descripción, comentario o nombres de los servicios asociados de forma instantánea.

## Scope

### In Scope
- **Frontend (`NovedadesParamPage.jsx`):**
  - Estado local `moduloFiltro` para capturar el texto ingresado por el usuario.
  - Input de búsqueda estilizado entre el botón "Nuevo módulo" y "Plantilla de importación" con placeholder descriptivo (ej. "Filtrar por módulo o servicio...").
  - Lógica de filtrado reactiva en memoria sobre el listado de módulos:
    - Normalización de texto (minúsculas y eliminación de diacríticos/tildes).
    - Coincidencia sobre: `item.descripcion`, `item.comentario`, y cualquiera de los `item.servicio_nombres`.
  - Mensaje amigable cuando el filtro no arroja resultados coincidentes.

### Out of Scope
- Modificaciones en endpoints de backend o esquemas de base de datos (el filtrado se ejecuta en cliente con la lista ya cargada de módulos y sus servicios asociados).

## Approach

1. Incorporar el input en la barra superior del tab `modulos` de `NovedadesParamPage.jsx`.
2. Computar `modulosFiltrados` aplicando una función de normalización de texto sobre la lista `modulos`.
3. Renderizar la lista a partir de `modulosFiltrados`.
4. Verificar con tests de frontend y build.
