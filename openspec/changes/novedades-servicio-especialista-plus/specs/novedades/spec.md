# Delta Spec: novedades — servicio Especialista + plus gated

## ADDED Requirements

### Requirement: Flag Especialista en servicio

Each Novedades **servicio** MUST have a boolean attribute **`especialista`** (UI label **Especialista**), editable in Parametrización alongside **Activo**. The flag MUST be independent of `activo`.

Migration and create defaults MUST set `especialista=false` for existing and new servicios. `admin`/`rrhh` MUST be able to toggle it on create/edit.

#### Scenario: Default OFF

- GIVEN migración o alta de servicio sin tildar Especialista
- WHEN se persiste el servicio
- THEN `especialista` MUST ser false

#### Scenario: Independiente de Activo

- GIVEN servicio inactivo
- WHEN se tilda Especialista
- THEN MUST persistirse true sin forzar Activo

### Requirement: Plus esp. en Detalle Capital Humano

In Capital Humano **Detalle** → tabla Cargas, module rows MUST show a column **Plus esp.** with **Sí** when the persisted assignment `valor` equals the module catalog value × **1.20** (same quantize as create), otherwise **—**. Novedad rows MUST show **—**. Excel export MUST NOT add this column.

#### Scenario: Detalle marca plus

- GIVEN asignación con valor 1200 y módulo catálogo 1000
- WHEN admin abre Detalle Cargas
- THEN Plus esp. MUST ser Sí

## MODIFIED Requirements

### Requirement: Plus 20% en módulos de especialistas

(Previously: plus if professional `es_especialista` only, on create and update.)

When **creating** a module assignment, the persisted `valor` MUST be catalog × **1.20** only if **both** `professional.es_especialista` **and** the assignment’s **servicio.especialista** are true; otherwise catalog value (quantize 0.01 as today). Novedades MUST NOT receive this factor.

When **updating** an assignment, the system MUST NOT re-apply the specialist plus: changing only `fecha_realizacion` MUST keep `valor`; if `modulo_id` changes, `valor` MUST become the new module’s catalog value **without** ×1.20. Historical rows are not bulk-recalculated in this change.

Capital Humano and exports MUST continue using persisted `valor` (no second multiplication). Multi-service modules: only the **servicio_id of the assignment** counts for the service flag.

#### Scenario: Especialista en servicio con flag

- GIVEN profesional especialista, servicio con Especialista ON, módulo 1000
- WHEN se crea la asignación en ese servicio
- THEN valor persistido MUST ser 1200

#### Scenario: Especialista en servicio sin flag

- GIVEN profesional especialista, servicio con Especialista OFF, módulo 1000
- WHEN se crea la asignación en ese servicio
- THEN valor persistido MUST ser 1000

#### Scenario: Edición no reaplica plus

- GIVEN asignación existente
- WHEN se actualiza solo la fecha
- THEN el valor MUST permanecer igual
