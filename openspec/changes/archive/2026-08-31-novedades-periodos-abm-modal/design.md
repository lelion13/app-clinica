# Design: novedades-periodos-abm-modal

## Technical Approach

Extend the existing `NovedadesPeriodo` management to provide full CRUD with modal-based workflows.

### 1. Backend Architecture

- **Schema:** `PeriodoUpdateRequest` en `backend/app/schemas/novedades.py`:
  ```python
  class PeriodoUpdateRequest(BaseModel):
      nombre: str | None = None
      fecha_inicio: date
      fecha_fin: date
  ```
- **Service Layer (`backend/app/services/novedades/cargas.py`):**
  - `update_periodo(db: Session, periodo_id: int, payload: PeriodoUpdateRequest, actor_id: int) -> NovedadesPeriodo`:
    1. Verifica que el período exista y no esté eliminado.
    2. Valida que `periodo.estado == PeriodoEstado.open` (si está cerrado, levanta HTTP 409).
    3. Valida que `payload.fecha_fin >= payload.fecha_inicio`.
    4. Consulta el valor mínimo y máximo de `fecha_realizacion` en `novedades_asignacion_modulo` y `novedades_novedad` activas del período:
       ```python
       # Si min(fecha_realizacion) < payload.fecha_inicio o max(fecha_realizacion) > payload.fecha_fin -> HTTP 422
       ```
    5. Actualiza campos y `updated_at`, `updated_by`.
  - `delete_periodo(db: Session, periodo_id: int, actor_id: int) -> None`:
    1. Verifica que el período exista.
    2. Cuenta si tiene registros en `novedades_asignacion_modulo`, `novedades_novedad`, `novedades_bono_cantidad`, `novedades_practica_cantidad`, `novedades_internacion_cantidad`, `novedades_ajuste_capital`.
    3. Si el recuento > 0, levanta HTTP 409 ("No se puede eliminar un período con cargas o producción asociada").
    4. Aplica soft-delete (`deleted_at = datetime.utcnow()`).
- **Router (`backend/app/api/routers/novedades.py`):**
  - `PUT /novedades/periodos/{periodo_id}`
  - `DELETE /novedades/periodos/{periodo_id}`

### 2. Frontend Architecture (`NovedadesParamPage.jsx`)

- **Tab Períodos:**
  - Encabezado con botón **"Nuevo período"** (estilo primario).
  - Modal **Crear período**:
    - `nombre` (opcional), `fecha_inicio`, `fecha_fin`.
    - Botones: Cancelar y Crear.
  - Lista de períodos:
    - Items con ID, nombre, rango de fechas y badge de estado (`open` / `closed`).
    - Botones por fila: `editar`, `cerrar`/`reabrir`, `eliminar`.
  - Modal **Editar período**:
    - Campos pre-poblados con datos actuales.
    - Botones: Cancelar y Guardar.
  - Modal **Eliminar período**:
    - Confirmación descriptiva: "¿Eliminar período #id · Nombre?".
    - Botones: Cancelar y Eliminar (danger).
