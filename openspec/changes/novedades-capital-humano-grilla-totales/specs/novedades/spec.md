# Delta Spec: novedades-capital-humano-grilla-totales

## ADDED Requirements

### Requirement: Pie de totales en grilla Capital Humano

The Capital Humano main grid MUST show a footer row that sums, for the **currently visible** rows (after text filter), these columns: **Total cargas**, **Ajustes**, **Total producción**, and **Total general**.

The footer cells for Legajo, Profesional, and Acciones MUST be empty (no “Total” label). The footer MUST remain visible when there are no visible rows, displaying `$0,00` (or equivalent `formatMoney(0)`) in each numeric column.

The footer MUST NOT appear in XLS exports. Backend aggregation for this footer is NOT required.

#### Scenario: Suma de visibles

- GIVEN dos profesionales visibles con totales generales 100 y 50
- WHEN se muestra la grilla
- THEN el pie MUST mostrar Total general 150 (y las sumas correspondientes de las otras columnas numéricas)

#### Scenario: Filtro reduce el pie

- GIVEN varias filas y filtro de texto que deja una sola
- WHEN se aplica el filtro
- THEN el pie MUST coincidir con los montos de esa única fila

#### Scenario: Sin filas

- GIVEN filtro o período sin filas visibles
- WHEN se muestra la grilla
- THEN el pie MUST seguir visible con $0,00 en las cuatro columnas numéricas
