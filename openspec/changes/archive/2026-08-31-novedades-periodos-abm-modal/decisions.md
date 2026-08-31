# Decisions: novedades-periodos-abm-modal

## Survey & Requirements Clarification

### Decision 1: Restricción al modificar fechas de un período con cargas
- **Decisión:** Validación estricta.
- **Detalle:** Se permite cambiar las fechas (`fecha_inicio` y/o `fecha_fin`) de un período siempre y cuando ninguna carga existente (asignación de módulo o novedad) en dicho período tenga una `fecha_realizacion` que quede fuera del nuevo rango. Si alguna carga queda fuera, se rechaza la modificación con un error 422 claro indicando el conflicto.

### Decision 2: Estado del período para edición
- **Decisión:** Solo períodos abiertos (`open`).
- **Detalle:** La edición (tanto de nombre como de fechas) solo está permitida si el período se encuentra en estado `open`. Los períodos cerrados (`closed`) permanecen congelados y de solo lectura.

### Decision 3: Eliminación de períodos (Soft-delete)
- **Decisión:** Permitir eliminación si no tiene cargas.
- **Detalle:** Se agrega botón y modal de confirmación de eliminación (soft-delete vía `deleted_at`). Solo se permite eliminar períodos que no tengan ninguna carga (`novedades_asignacion_modulo`, `novedades_novedad`, snapshots de bonos/prácticas/internaciones ni ajustes) asociada. Si tiene cargas, se rechaza.

### Decision 4: Modalidad y Formato de UI (copiado de Módulos)
- **Decisión:** Formato consistente con el tab de Módulos:
  - Botón superior **"Nuevo período"** que abre modal para crear (en reemplazo del formulario inline).
  - Modal **"Editar período"** (nombre, fecha inicio, fecha fin).
  - Modal de confirmación **"Eliminar período"**.
  - Botones de acción en cada fila de la lista: `editar`, `cerrar`/`reabrir`, `eliminar`.
