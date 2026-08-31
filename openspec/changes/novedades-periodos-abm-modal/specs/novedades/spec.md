# Delta Spec: novedades-periodos-abm-modal

## MODIFIED Requirements

### Requirement: Períodos de carga

The system MUST allow `admin` and `rrhh` to manage **Períodos** in Parametrización using consistent modal-based interactions identical to the Módulos pattern.

The system MUST support:
1. **Creación con modal:** Botón superior **"Nuevo período"** que abre modal con campos `nombre` (opcional), `fecha_inicio` y `fecha_fin`.
2. **Edición con modal (`PUT /novedades/periodos/{id}`):**
   - Permitida únicamente cuando el período está en estado **`open`** (`closed` retorna 409).
   - Permite modificar `nombre`, `fecha_inicio` y `fecha_fin`.
   - `fecha_fin` MUST ser posterior o igual a `fecha_inicio`.
   - Validación de cargas: Si el período contiene cargas existentes (`novedades_asignacion_modulo` o `novedades_novedad`), ninguna de sus fechas de realización puede quedar fuera del nuevo rango `[fecha_inicio, fecha_fin]`. En caso de conflicto, la API MUST responder 422 detallando el conflicto.
3. **Eliminación soft-delete (`DELETE /novedades/periodos/{id}`):**
   - Permitida únicamente si el período NO tiene cargas asociadas (módulos, novedades, bonos, prácticas, internaciones, ajustes).
   - Si tiene cargas asociadas, la API MUST responder 409/422 impidiendo la eliminación.
   - En la UI, la acción MUST requerir confirmación en modal ("Eliminar período").
4. **Cierre y reapertura:**
   - Botón contextual `cerrar` / `reabrir` por fila, manteniendo la regla de que solo puede existir un único período abierto simultáneamente.

#### Scenario: Edición exitosa de período abierto sin conflicto
- GIVEN un período en estado `open` con rango `2026-08-01` a `2026-08-31`
- AND sus cargas existentes tienen `fecha_realizacion` entre `2026-08-05` y `2026-08-20`
- WHEN admin/rrhh actualiza el período con nuevo rango `2026-08-01` a `2026-08-25`
- THEN el período se actualiza correctamente y se persiste en base de datos

#### Scenario: Rechazo de edición por cargas fuera de nuevo rango
- GIVEN un período en estado `open` con una carga registrada el `2026-08-28`
- WHEN admin/rrhh intenta achicar el período a `2026-08-01` hasta `2026-08-20`
- THEN la API rechaza la actualización con error 422 indicando que existen cargas fuera del rango propuesto
- AND las fechas del período permanecen sin cambios

#### Scenario: Rechazo de edición en período cerrado
- GIVEN un período en estado `closed`
- WHEN se intenta invocar `PUT /novedades/periodos/{id}`
- THEN la API rechaza la solicitud con error 409/422

#### Scenario: Eliminación de período sin cargas
- GIVEN un período recién creado sin ninguna asignación de módulo ni novedad
- WHEN admin pulsa "eliminar" y confirma en el modal
- THEN el período es marcado como soft-deleted (`deleted_at != null`)
- AND deja de aparecer en el listado y selectores

#### Scenario: Rechazo de eliminación de período con cargas
- GIVEN un período que tiene al menos una carga registrada
- WHEN se intenta eliminar el período
- THEN la API rechaza la eliminación con error 409
- AND el período se mantiene activo en el sistema
