# Decisions: novedades-capital-humano-export-liquidacion

## Survey (closed)

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Botón vs exports existentes | **A** — Nuevo botón "Descargar liquidación"; no tocar ni reemplazar exports actuales |
| Q2 | Cómo entra Producción | **C** — Las **cargas** definen las filas por concepto; bonos/prácticas/internaciones se **suman** a esas filas. Si hay varios conceptos de la **misma empresa**, dividir en partes iguales |
| Q3 | Solo producción (sin cargas) | **B** — Sí exportar, con conceptos fijos por empresa+servicio especial |
| Q4 | Conceptos fijos sin cargas | CMG DEA/CAI=**90**, CMG DEP/CAP=**91**, SC(CHI) DEA/CAI=**123**, SC(CHI) DEP/CAP=**122** |
| Q5 | Cuándo aplicar conceptos fijos | **A** — Solo si el profesional **no tiene cargas** |
| Q6 | Sin cargas y sin DEA/DEP/CAP/CAI | **B** — No exportar |
| Q7 | Ajustes (Agregar importe) | **A** — Prorratear en partes iguales entre conceptos de carga; si no hay cargas, entre conceptos fijos generados; si no hay ninguno, no exportar el ajuste |
| Q8 | Producción de empresa distinta a cargas | **C** — Forzar a los conceptos de carga existentes aunque sean de otra empresa (fallback si no hay conceptos de esa empresa) |
| Q9 | Agrupación | **A** — Una fila por `empresa + legajo + concepto` (montos sumados) |
| Q10 | Servicio sin concepto_liquidacion | **B** — Bloquear toda la exportación avisando qué servicio(s) no tienen concepto |
| Q11 | Formato monto | **C** — Tal cual en el sistema (Decimal / decimales permitidos) |
| Q12 | Varios especiales sin cargas | **A** — Una fila por concepto fijo presente; producción de esa empresa en partes iguales |
| Q13 | Prefijo desconocido | **A** — Solo `SC…` → CHI; cualquier otro (incl. vacío) → CMG |

## Derived business rules

### Empresa from concepto (column `empresa`)
- `concepto > 100` → `CHI`
- `concepto < 100` → `CMG`
- `concepto == 100` → treat as `CMG` (not strictly greater than 100)

### Empresa from production source (for bucketing amounts before merge)
- Read `centro` (bonos/prácticas) or `sucursal` (internaciones)
- Starts with `SC` (case-insensitive, trim) → CHI
- Otherwise → CMG

### Eligibility for valorized production
Reuse Capital Humano eligibility already in place (módulos → all; sin módulos → special bonos DEA/DEP/CAP/CAI + prácticas/internaciones per existing rules). Export uses the **same valorized amounts** as the grid for the selected closed period.

### Period gate
Only **closed** periods may be exported. Open period → reject (UI disable + API 409/422).
