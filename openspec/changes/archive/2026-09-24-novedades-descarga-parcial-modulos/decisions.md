# Decisions: novedades-descarga-parcial-modulos

| # | Topic | Choice |
|---|--------|--------|
| Q1 | Fecha de filtro | **A** — `fecha_realizacion` |
| Q2 | Inclusión rango | **A** — desde/hasta inclusive; exigir desde ≤ hasta |
| Q3 | Columnas grilla modal | **A** — legajo · nombre · total cargas (+ Detalle) |
| Q4 | Qué es “cargas” | **A** — módulos + novedades (como CH), filtrados por fechas |
| Q5 | Sin cargas en rango | **A** — no aparece en grilla ni Excel |
| Q6 | Detalle expandido | **A** — misma tabla Cargas de CH, solo ítems del rango |
| Q7 | Excel | **C** — dos hojas: resumen + detalle |
| Q8 | Quién puede usar | **A** — `admin` y `rrhh` |
| Q9 | Carga grilla modal | **A** — automática al tener desde/hasta válidos |
| Q10 | Fechas iniciales | **A** — vacías al abrir |
| Q11 | Botón Descargar | **A** — solo con fechas válidas y ≥1 fila |
| Q12 | Texto botón | **B** — `Descarga parcial de módulos` |
| Q13 | Expansión Detalle | **A** — solo una fila expandida a la vez |
| Q14 | Filtro/pie modal | **A** — sin filtro texto ni pie de totales |
| Q15 | API | **B** — reusar grilla + export existentes con filtros de fecha |
| Q16 | Excel 2 hojas | **A** — extender `export.xlsx`: con fechas → 2 hojas; sin fechas → 1 hoja |
| Q17 | Período cerrado API | **B** — solo UI exige cerrado; API acepta fechas también si abierto |
| Q18 | Nombre archivo | **B** — `descarga-parcial-modulos_{desde}_{hasta}.xlsx` |
| Q19 | Total cargas | **A** — suma de `valor` (como CH) |
| Q20 | Fechas vs período | **B** — solo UI min/max; API no valida contra período |
| Q21 | Nombres hojas | **A** — `Resumen` y `Detalle` |

## Survey status
CLOSED
