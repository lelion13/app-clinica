# Delta Spec: novedades-capital-humano-importe-descontar

## ADDED Requirements

### Requirement: UI Importe a descontar / Anular descuento

Capital Humano MUST show **Importe a descontar** for `admin`/`rrhh` **before** **Descargar liquidación**. The control MUST require a selected **closed** period.

When the closed period has an active discount-import lot, the control MUST show **Anular descuento** instead and MUST NOT allow a new import until that lot is annulled.

**Anular descuento** MUST soft-delete only adjustments belonging to that import lot (MUST NOT remove manual **Agregar importe** adjustments).

#### Scenario: Botón orden y período abierto

- GIVEN período `open` seleccionado
- WHEN admin ve la barra de acciones
- THEN MUST ver Importe a descontar antes de Descargar liquidación
- AND ambos MUST permanecer deshabilitados o rechazar la acción

#### Scenario: Anular solo el lote

- GIVEN período cerrado con lote importado y un ajuste manual
- WHEN admin pulsa Anular descuento
- THEN MUST eliminarse solo los ajustes del lote
- AND el ajuste manual MUST permanecer
- AND el botón MUST volver a Importe a descontar

### Requirement: Import Excel Importe a descontar

Import MUST accept `.xlsx` whose headers match **exactly** (text and presence): `Legajo`, `Nombre y Apellido`, `Sector`, `Monto`.

Each data row MUST create one or more adjustments equivalent to **Agregar importe**:
- Match professional by **legajo** only (Nombre/Sector MUST NOT be validated against catalog)
- Legajo MUST appear on the Capital Humano grid for that period (cargas and/or producción)
- `importe` MUST be `-abs(Monto)` (never double-negate)
- `comentario` MUST be `Legajo - Nombre y Apellido - Sector - {importe negativizado}`, truncated to 500 chars if longer
- Monto empty or zero MUST be an error

Duplicate legajo in the file, unknown/absent-from-grid legajo, open period, or an existing active lot MUST fail validation.

Import MUST be all-or-nothing: if any row/legajo fails, MUST create **no** adjustments. The UI MUST show a centered modal listing **all** errors together.

#### Scenario: Import OK un servicio

- GIVEN período cerrado sin lote, legajo en grilla con un servicio de cargas, Excel válido Monto=500
- WHEN admin importa
- THEN MUST crearse ajuste(s) con importe -500 y comentario con monto negativizado
- AND el botón MUST pasar a Anular descuento

#### Scenario: Error agrega todos y no impacta

- GIVEN Excel con un legajo inexistente y otro duplicado
- WHEN admin importa
- THEN MUST no crearse ningún ajuste
- AND el modal MUST listar ambos errores

#### Scenario: Re-import bloqueado

- GIVEN período cerrado con lote activo
- WHEN admin intenta importar otro Excel
- THEN MUST rechazarse hasta anular

### Requirement: Reparto multi-servicio (waterfill)

When the professional has cargas in multiple services, the absolute discount MUST be allocated across services by creating one adjustment per consumed service (`servicio_id` set):
1. Group period cargas by service; order by cargas amount descending (ties MAY be any order)
2. Fill each service up to its cargas amount
3. If absolute discount > sum(cargas) but ≤ cargas+producción, remaining MUST go to the **last** service in that ordered list
4. If absolute discount > cargas+producción, OR projected total general (`cargas + existing ajustes + producción + new discount`) would be negative → that legajo MUST error (blocks whole import)

When the professional has **no cargas** (producción only on the grid), MUST create a single adjustment with `servicio_id` null for the full negativized amount (still subject to the cargas+producción cap and total-general rule).

#### Scenario: Waterfill dos servicios

- GIVEN servicios A cargas=1000, B cargas=800, descuento 1500, producción 0, sin ajustes previos
- WHEN importa
- THEN MUST crear ajuste -1000 en A y -500 en B

#### Scenario: Resto sobre producción al último

- GIVEN suma cargas=1800, producción=200, descuento 2000
- WHEN importa
- THEN MUST aplicar el sobrante 200 al último servicio de la lista ordenada
- AND MUST NOT fallar por tope

#### Scenario: Solo producción

- GIVEN profesional solo producción 300, descuento 100
- WHEN importa
- THEN MUST crear un ajuste -100 sin servicio

#### Scenario: Tope excedido bloquea

- GIVEN cargas+producción=1000, descuento 1001
- WHEN importa
- THEN MUST fallar ese legajo
- AND no MUST impactarse ningún legajo del archivo

## MODIFIED Requirements

### Requirement: Ajustes en liquidación

(Previously: all adjustments split equally across liquidación conceptos.)

Adjustments with a non-null `servicio_id` MUST be applied to that service’s liquidación concepto (the `concepto_liquidacion` of that service). Adjustments with null `servicio_id` MUST continue to split equally across the professional’s liquidación conceptos (carga-derived or fixed conceptos when no cargas). They MUST NOT create a separate concepto by themselves.

#### Scenario: Ajuste con servicio va al concepto

- GIVEN profesional con conceptos 50 (svc A) y 150 (svc B) y ajuste -500 con servicio A
- WHEN exporta liquidación
- THEN el concepto 50 MUST recibir -500
- AND el concepto 150 MUST NOT recibir parte de ese ajuste

#### Scenario: Ajuste sin servicio se reparte

- GIVEN profesional con conceptos 50 y 150 y ajuste -200 sin servicio
- WHEN exporta liquidación
- THEN cada fila MUST recibir -100
