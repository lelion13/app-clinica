# Delta Spec: novedades-capital-humano-ajuste-mas-menos

## ADDED Requirements

### Requirement: UI Ajuste +/- / Anular Ajuste +/-

Capital Humano MUST show **Ajuste +/-** for `admin`/`rrhh` **immediately to the right** of **Importe a descontar** / **Anular descuento**, and **before** **Descargar liquidación**. The control MUST require a selected **closed** period (same enablement rules as Importe a descontar for open vs closed).

When the closed period has an active Ajuste +/- import lot, the control MUST show **Anular Ajuste +/-** instead and MUST NOT allow a new Ajuste +/- import until that lot is annulled.

**Anular Ajuste +/-** MUST soft-delete only adjustments belonging to that Ajuste +/- import lot. It MUST NOT remove:
- adjustments from an **Importe a descontar** lot
- manual **Agregar importe** adjustments

An active Importe a descontar lot MUST NOT block Ajuste +/- import, and an active Ajuste +/- lot MUST NOT block Importe a descontar import (lots MAY coexist).

#### Scenario: Orden de botones

- GIVEN período cerrado seleccionado
- WHEN admin ve la barra de acciones
- THEN MUST ver Importe a descontar (o Anular descuento), luego Ajuste +/- (o Anular Ajuste +/-), luego Descargar liquidación

#### Scenario: Anular solo lote Ajuste +/-

- GIVEN período cerrado con lote descuento, lote Ajuste +/- y un ajuste manual
- WHEN admin pulsa Anular Ajuste +/-
- THEN MUST eliminarse solo los ajustes del lote Ajuste +/-
- AND el lote descuento y el ajuste manual MUST permanecer
- AND el botón MUST volver a Ajuste +/-

#### Scenario: Lotes coexisten

- GIVEN período cerrado con lote Importe a descontar activo
- WHEN admin importa un Excel válido de Ajuste +/-
- THEN MUST crearse el lote Ajuste +/-
- AND el lote descuento MUST permanecer activo

### Requirement: Import Excel Ajuste +/-

Import MUST accept `.xlsx` whose headers match **exactly** (text and presence): `Legajo`, `Nombre y Apellido`, `Sector`, `Monto`.

Each data row MUST create one or more adjustments equivalent to **Agregar importe**, with signed `importe` from `Monto`:
- Match professional by **legajo** only (Nombre/Sector MUST NOT be validated against catalog)
- Legajo MUST appear on the Capital Humano grid for that period (cargas and/or producción)
- If `Monto` is negative → `importe` MUST be `-abs(Monto)` (never double-negate)
- If `Monto` is positive or written with `+` → `importe` MUST be `+abs(Monto)`
- Unsigned numeric positive (e.g. `500`) MUST be treated as positive (not empty)
- `comentario` MUST be `Legajo - Nombre y Apellido - Sector - {importe with sign}`, truncated to 500 chars if longer
- Monto empty or zero MUST be an error

Duplicate legajo in the file, unknown/absent-from-grid legajo, open period, or an existing **active Ajuste +/- lot** MUST fail validation.

Import MUST be all-or-nothing: if any row/legajo fails, MUST create **no** Ajuste +/- adjustments. The UI MUST show a centered modal listing **all** errors together.

#### Scenario: Import positivo un servicio

- GIVEN período cerrado sin lote Ajuste +/-, legajo en grilla con un servicio de cargas, Excel Monto=500
- WHEN admin importa Ajuste +/-
- THEN MUST crearse ajuste(s) con importe 500 y comentario con 500
- AND el botón MUST pasar a Anular Ajuste +/-

#### Scenario: Import negativo igual descontar

- GIVEN período cerrado, legajo válido, Excel Monto=-500 (o celda negativa)
- WHEN admin importa Ajuste +/-
- THEN MUST crearse ajuste(s) con importe -500
- AND MUST aplicarse tope cargas+producción y waterfill como Importe a descontar

#### Scenario: Error agrega todos y no impacta

- GIVEN Excel con un legajo inexistente y otro duplicado
- WHEN admin importa Ajuste +/-
- THEN MUST no crearse ningún ajuste de este import
- AND el modal MUST listar ambos errores

#### Scenario: Re-import Ajuste +/- bloqueado

- GIVEN período cerrado con lote Ajuste +/- activo
- WHEN admin intenta importar otro Excel de Ajuste +/-
- THEN MUST rechazarse hasta anular ese lote

### Requirement: Reparto multi-servicio Ajuste +/- (waterfill)

When the professional has cargas in multiple services, the **absolute** amount of the row MUST be allocated across services by creating one adjustment per consumed service (`servicio_id` set), using the same ordering as Importe a descontar:
1. Group period cargas by service; order by cargas amount descending (ties MAY be any order)
2. Fill each service up to its cargas amount (with the row’s sign on each partial)
3. Remaining absolute amount after filling cargas:
   - **Negative row:** if absolute amount ≤ cargas+producción, remaining MUST go to the **last** service in that ordered list; if absolute amount > cargas+producción, OR projected total general (`cargas + existing ajustes + producción + new row effect`) would be negative → that legajo MUST error (blocks whole Ajuste +/- import)
   - **Positive row:** remaining MUST go to the **last** service in that ordered list with **no** cargas+producción cap and **no** “total too high” error

When the professional has **no cargas** (producción only on the grid):
- MUST create a single adjustment with `servicio_id` null for the full signed amount
- **Negative:** still subject to the cargas+producción cap and total-general rule
- **Positive:** no cap

#### Scenario: Waterfill positivo dos servicios

- GIVEN servicios A cargas=1000, B cargas=800, Monto +1500, producción 0
- WHEN importa Ajuste +/-
- THEN MUST crear ajuste +1000 en A y +500 en B

#### Scenario: Positivo sin tope sobre producción

- GIVEN suma cargas=1800, producción=200, Monto +5000
- WHEN importa Ajuste +/-
- THEN MUST aplicar waterfill sobre cargas y el resto al último servicio
- AND MUST NOT fallar por tope

#### Scenario: Negativo tope excedido bloquea

- GIVEN cargas+producción=1000, Monto -1001
- WHEN importa Ajuste +/-
- THEN MUST fallar ese legajo
- AND no MUST impactarse ningún legajo del archivo Ajuste +/-

#### Scenario: Solo producción positivo

- GIVEN profesional solo producción 300, Monto +100
- WHEN importa Ajuste +/-
- THEN MUST crear un ajuste +100 sin servicio

## MODIFIED Requirements

### Requirement: UI Importe a descontar / Anular descuento

(Previously: Importe a descontar appears before Descargar liquidación; Anular only that discount lot.)

Behavior of Importe a descontar / Anular descuento MUST remain as specified, with these clarifications:
- **Ajuste +/-** MUST appear immediately after this control and before Descargar liquidación
- An active Ajuste +/- lot MUST NOT change Importe a descontar enablement or annulation scope
- **Anular descuento** MUST continue to soft-delete only the discount-import lot (MUST NOT remove Ajuste +/- lot adjustments)

#### Scenario: Anular descuento no toca Ajuste +/-

- GIVEN período cerrado con ambos lotes activos
- WHEN admin pulsa Anular descuento
- THEN MUST eliminarse solo el lote descuento
- AND el lote Ajuste +/- MUST permanecer
