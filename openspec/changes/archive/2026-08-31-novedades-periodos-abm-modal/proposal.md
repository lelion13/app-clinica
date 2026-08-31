# Proposal: novedades-periodos-abm-modal

## Intent

Modernizar la gestión de **Períodos** en Parametrización de Novedades adoptando la misma modalidad y formato de botones/modales que **Módulos** (modal de creación, modal de edición de datos/fechas con validación de coherencia con cargas existentes, y modal de eliminación soft-delete cuando no existan cargas asociadas).

## Scope

### In Scope
- **Backend:**
  - Endpoint `PUT /novedades/periodos/{periodo_id}`: Actualizar `nombre`, `fecha_inicio`, `fecha_fin`.
    - Validación: Período debe estar en estado `open`.
    - Validación: `fecha_fin >= fecha_inicio`.
    - Validación de coherencia: Si existen cargas con `fecha_realizacion`, ninguna puede quedar fuera del nuevo rango `[fecha_inicio, fecha_fin]`.
  - Endpoint `DELETE /novedades/periodos/{periodo_id}`: Soft-delete del período.
    - Validación: No debe tener cargas asignadas (módulos, novedades, bonos, prácticas, internaciones ni ajustes).
  - Schema Pydantic `PeriodoUpdateRequest`.
- **Frontend (`NovedadesParamPage.jsx`):**
  - Reemplazo del formulario inline de alta por botón superior **"Nuevo período"** y modal de alta.
  - Modales:
    - Modal **"Nuevo período"** (Nombre opcional, Fecha inicio, Fecha fin, Cancelar / Crear).
    - Modal **"Editar período"** (Nombre, Fecha inicio, Fecha fin, Cancelar / Guardar).
    - Modal **"Eliminar período"** (Confirmación con texto informativo y Cancelar / Eliminar).
  - Botones de acción en cada fila de la lista de períodos: `editar`, `cerrar`/`reabrir`, `eliminar`.

### Out of Scope
- Edición de períodos en estado `closed` (deben reabrirse previamente).
- Re-asignación masiva de fechas de cargas al cambiar el rango del período.

## Approach

1. Implementar schemas y servicios backend en `app/services/novedades/cargas.py` y endpoints en `app/api/routers/novedades.py`.
2. Añadir tests unitarios en pytest que cubran:
   - Edición de fechas válida.
   - Rechazo de edición si el período está cerrado.
   - Rechazo de edición si existen cargas con fechas que quedarían fuera del nuevo rango.
   - Eliminación exitosa de período sin cargas.
   - Rechazo de eliminación de período con cargas.
3. Actualizar la interfaz de usuario en `NovedadesParamPage.jsx` siguiendo exactamente el estilo y modales de Módulos/Feriados.
