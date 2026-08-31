# Tasks: novedades-periodos-abm-modal

## Phase 1: Backend Schemas, Service & Endpoints
- [ ] 1.1 Agregar schema `PeriodoUpdateRequest` en `backend/app/schemas/novedades.py`.
- [ ] 1.2 Implementar `update_periodo` y `delete_periodo` con validaciones de estado y fechas de cargas en `backend/app/services/novedades/cargas.py`.
- [ ] 1.3 Exponer endpoints `PUT /novedades/periodos/{periodo_id}` y `DELETE /novedades/periodos/{periodo_id}` en `backend/app/api/routers/novedades.py`.

## Phase 2: Backend Unit Tests
- [ ] 2.1 Agregar tests unitarios para edición válida, rechazo por período cerrado, rechazo por cargas fuera de rango y eliminación condicional en `backend/tests/test_cargas.py`.

## Phase 3: Frontend UI en Parametrización
- [ ] 3.1 Actualizar tab Períodos en `frontend/src/pages/novedades/NovedadesParamPage.jsx` con botón superior "Nuevo período" y modal de creación.
- [ ] 3.2 Implementar modal "Editar período" y modal de confirmación "Eliminar período".
- [ ] 3.3 Integrar botones de acción (`editar`, `cerrar`/`reabrir`, `eliminar`) en cada fila de la lista.

## Phase 4: Verification & Documentation
- [ ] 4.1 Ejecutar suite completa de tests de backend (`pytest`) y build de frontend (`npm run build`).
- [ ] 4.2 Documentar cambios y preparar reporte de verificación.
