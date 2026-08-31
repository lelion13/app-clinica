# Decisions: novedades-modulos-filtro-ui

## Survey & Requirements Clarification

### Decision 1: Alcance de coincidencia del filtro
- **Decisión:** Buscar en descripción de módulo, comentario y nombres de servicios asociados.
- **Detalle:** Si el usuario escribe el nombre de un servicio (ej. "Traumatología", "Guardia"), se listan todos los módulos asignados a ese servicio. Si escribe parte del nombre o comentario del módulo (ej. "SADOFE", "Especial"), filtra los módulos correspondientes.

### Decision 2: Normalización de búsqueda
- **Decisión:** Insensible a mayúsculas/minúsculas y a acentos/tildes.
- **Detalle:** La búsqueda normaliza cadenas (removiendo diacríticos y transformando a minúsculas) para que escribir "clinica", "clínica", "CLINICA" o "trauma" encuentre resultados de forma inmediata e intuitiva.

### Decision 3: Ubicación visual y comportamiento
- **Decisión:** Input de texto ubicado en la barra de herramientas del tab Módulos, entre el botón "Nuevo módulo" y el botón "Plantilla de importación".
- **Detalle:** Si no hay resultados que coincidan con el filtro, se muestra un mensaje informativo ("No se encontraron módulos que coincidan con la búsqueda").
