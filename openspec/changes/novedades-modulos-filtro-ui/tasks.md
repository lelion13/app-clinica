# Tasks: novedades-modulos-filtro-ui

## Phase 1: Frontend Implementation
- [ ] 1.1 Agregar estado `moduloFiltro` y función de normalización en `frontend/src/pages/novedades/NovedadesParamPage.jsx`.
- [ ] 1.2 Computar `modulosFiltrados` evaluando descripción, comentario y servicios asociados de manera insensible a mayúsculas y acentos.
- [ ] 1.3 Insertar el `<input>` de filtro entre el botón "Nuevo módulo" y "Plantilla de importación".
- [ ] 1.4 Renderizar `modulosFiltrados` en la lista y mostrar mensaje de estado vacío cuando no haya coincidencias.

## Phase 2: Verification & Build
- [ ] 2.1 Ejecutar suite de frontend `npm run build`.
- [ ] 2.2 Ejecutar suite de backend `pytest`.
- [ ] 2.3 Generar `verify-report.md`.
