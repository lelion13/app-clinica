# Delta: novedades / módulos edición

## MODIFIED Requirements

### Requirement: Servicios y módulos

The system MUST provide ABM of **servicios** (id, nombre, activo, **valor_hora**) and **módulos** (id, descripción, comentario, valor ARS, **produccion** boolean) with **N:N** association to services. Admin and `rrhh` MUST manage them; `jefe_medico` MUST NOT.

Modules MUST support:
- Create with optional `produccion` (default false) and at least one `servicio_id`
- Update of data fields (descripción, comentario, valor, produccion) without changing associations
- Replace of service associations (including empty set) via a dedicated endpoint
- Param UI: edit modal (Cancelar/Guardar) and services modal (Cancelar/Aceptar); list buttons `editar` / `servicios`

#### Scenario: Alta módulo con produccion

- GIVEN `rrhh` autenticado
- WHEN crea módulo con `produccion=false` (default) y uno o más servicios
- THEN el módulo se persiste con `produccion=false`

#### Scenario: Editar datos sin tocar servicios

- GIVEN módulo asociado a servicios S1,S2
- WHEN admin guarda el modal editar cambiando valor y `produccion`
- THEN descripción/comentario/valor/produccion se actualizan y las asociaciones permanecen

#### Scenario: Desasociar todos los servicios

- GIVEN módulo con servicios
- WHEN admin acepta el modal servicios con ningún checkbox
- THEN el módulo queda sin asociaciones activas (“sin asociar”)

### Requirement: Verificación de producción en Carga (interacción con flag módulo)

When creating a carga that includes a **módulo** with `produccion=false`, the UI MUST NOT call the external `tiene-produccion` check for that submit. When the carga is only a novedad, or the selected módulo has `produccion=true`, the existing check (and force-load modal when false) MUST apply. Editing `fecha_realizacion` MUST continue to require the external check.

#### Scenario: Carga módulo sin producción propia

- GIVEN módulo M con `produccion=false`
- WHEN admin/jefe carga solo M (o M + novedad) en una fecha
- THEN MUST NOT llamar `GET .../bonos/tiene-produccion` y MUST permitir el POST

#### Scenario: Carga solo novedad

- GIVEN formulario sin módulo
- WHEN se carga solo novedad
- THEN MUST verificar producción externa como hoy
