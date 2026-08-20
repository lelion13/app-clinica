# Delta: novedades

## MODIFIED Requirements

### Requirement: Columnas de bonos en grilla Capital Humano

The main Capital Humano grid MUST remain one row per professional. In addition to professionals with cargas/ajustes, it MUST include professionals with bonos-only when, for the selected period, they have at least one bonos option whose `servicio` value is exactly one of: `DEA`, `DEP`, `CAP`, `CAI`.

For these promoted rows:
- `monto_cargas` MUST be 0 when no cargas exist.
- `monto_ajustes` MUST be 0 when no ajustes exist.
- `monto_total` MUST remain `monto_cargas + monto_ajustes` (bonos not monetized in this change).

#### Scenario: Solo bonos CAP entra a grilla

- GIVEN profesional P con bonos en período y opción con `servicio = CAP`
- AND P no tiene cargas ni ajustes
- WHEN se lista Capital Humano
- THEN P MUST aparecer en la grilla principal
- AND `monto_total` MUST ser 0

#### Scenario: Solo bonos servicio no especial no entra

- GIVEN profesional Q con bonos en período y opciones sin `DEA|DEP|CAP|CAI`
- AND Q no tiene cargas ni ajustes
- WHEN se lista Capital Humano
- THEN Q MUST NOT aparecer en la grilla principal

### Requirement: Modal solo bonos

The Solo bonos modal MUST list only professionals with bonos persisted for the period that are not present in the main grid after applying the special-service promotion rule.

#### Scenario: Promovido excluido de Solo bonos

- GIVEN profesional P con bonos-only y opción `servicio = DEA`
- WHEN se abre modal Solo bonos
- THEN P MUST NOT aparecer en el modal

### Requirement: Pantalla Capital Humano

The Capital Humano UI MUST remove the service selector from this screen and operate as “todos los servicios” from UI perspective. Backend endpoint compatibility with optional `servicio_id` MAY remain unchanged.

#### Scenario: UI sin filtro por servicio

- GIVEN usuario admin/rrhh en Capital Humano
- WHEN visualiza filtros
- THEN MUST ver selector de período y búsqueda de texto
- AND MUST NOT ver selector de servicio
