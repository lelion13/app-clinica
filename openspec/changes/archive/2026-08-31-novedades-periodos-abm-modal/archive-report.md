# Archive Report: novedades-periodos-abm-modal

## Change Summary
- **Change Name:** `novedades-periodos-abm-modal` (ABM modal de Períodos en Parametrización)
- **Target Spec:** `openspec/specs/novedades/spec.md`
- **Archive Date:** 2026-08-31

## Delivered Capabilities
1. **Modal de creación de período:**
   - Botón superior "Nuevo período" en Parametrización tab Períodos.
   - Modal con campos de nombre opcional, fecha de inicio y fecha de fin.
2. **Modal de edición de período (`PUT /novedades/periodos/{id}`):**
   - Habilitado solo para períodos en estado `open`.
   - Permite modificar nombre y fechas (`fecha_inicio` y `fecha_fin`).
   - Validación estricta: rechaza con 422 si existen cargas asociadas cuyas fechas de realización queden fuera del nuevo rango propuesto.
3. **Modal de eliminación de período (`DELETE /novedades/periodos/{id}`):**
   - Soft-delete seguro (`deleted_at`).
   - Validación: solo permite eliminar períodos sin cargas activas (módulos, novedades, bonos, prácticas, internaciones ni ajustes).
4. **UI Consistente:**
   - Adopta el formato visual y comportamiento de botones/modales de Módulos y Feriados.
   - Botones contextuales por fila (`editar`, `cerrar`/`reabrir`, `eliminar`).

## Verification Summary
- **Backend Tests:** 148 passed (`pytest`).
- **Frontend Build:** Vite build exitoso (`npm run build`).
