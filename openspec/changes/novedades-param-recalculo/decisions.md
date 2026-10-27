# Decisions: novedades-param-recalculo

## Locked (from product, before survey)

| Topic | Decision |
|--------|----------|
| Entry | En **Parametrización** Novedades, después de **Feriados** |
| Acción | Recalcular valor de **hora** (novedades) y/o **módulo** ya cargados, según catálogo actual |
| Filtros UI | Modo: solo horas / solo módulos / ambos + selección de período |
| Guard | Si el valor de catálogo no cambió vs lo persistido → no permitir actualizar |
| Preview | Antes de aplicar: resumen importe actual vs nuevo (por módulo y por horas) |
| Roles | Mismos que Parametrización (`admin` / `rrhh`) |
| Branch | `medicos` |

## Survey (open)

| # | Topic | Options | Choice |
|---|--------|---------|--------|
| Q1 | Control “Recálculo” en Param | A = pestaña nueva · B = botón suelto · C = otro | **A** — pestaña nueva después de Feriados |
| Q2 | Período elegible | A = solo abierto · B = abierto o cerrado · C = solo cerrado | **B** — abierto o cerrado |
| Q3 | Alcance de filas | A = todas las cargas del período · B = +servicio · C = +profesional | **A** — todas las cargas del período |
| Q4 | Plus especialista al recalcular módulos | A = misma regla que al cargar · B = sin plus · C = conservar flag de la fila | **A** — misma regla que al cargar (×1.20 si aplica) |
| Q5 | Si ninguna fila cambia de valor | A = bloquear Apply · B = permitir no-op · C = otro | **A** — bloquear Apply (“no hay cambios”) |
| Q6 | Resumen previo (granularidad) | A = totales globales · B = por módulo de catálogo + bloque horas · C = por profesional | **B** — por módulo de catálogo + bloque horas |
| Q7 | Flujo UI | A = Preview → Confirmar · B = Apply con “¿Seguro?” · C = preview siempre visible | **A** — Vista previa → Confirmar actualización |
| Q8 | Recálculo de novedades (horas) | A = mantiene horas; recalcula importe · B = también cambia cantidad · C = otro | **A** — mantiene `horas`; importe = horas × valor_hora servicio (signo por tipo) |
| Q9 | Filas anuladas / soft-delete | A = excluir · B = incluir · C = otro | **A** — excluir del preview y del apply |

## Survey status

**Closed** (Q1–Q9).
