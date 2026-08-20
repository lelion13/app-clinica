# Decisions: novedades-produccion-valor-bonos

Survey: **una pregunta a la vez**. Estado: **CLOSED** (2026-08-19).

## Contexto heredado (sin cambios)

Se mantiene vigente lo definido en `capital-humano-bonos-resumen` y `capital-humano-bonos-servicios-especiales` para:
- importación y persistencia de bonos por período
- columnas dinámicas por opción `centro|servicio|semana|horario`
- modal Solo bonos y regla DEA/DEP/CAP/CAI
- congelamiento en período cerrado

## Nuevas decisiones

### Q1 — Clave de match tarifa ↔ bono importado
**Elegido: match exacto por 4 campos** — `centro`, `servicio`, `semana`, `horario` (misma clave que columna dinámica de bonos).

### Q2 — Unicidad del catálogo
**Elegido: C** — Una sola tarifa por combinación de 4 campos; para cambiar el valor se **edita** la fila existente (no duplicar).

### Q3 — Campos de cada fila de Producción
**Elegido: A** — Solo los 4 campos de match + `valor_unitario` obligatorio entero ≥ 0. Sin descripción, sin checkbox activo.

### Q4 — Presentación en grilla Capital Humano
**Elegido: B** — Por cada opción de bono: **dos columnas** (cantidad y subtotal = cantidad × valor).

### Q5 — Opción importada sin tarifa
**Elegido: B** — Mostrar cantidad; subtotal = **0**; aviso en UI; **no bloquea** import ni grilla.

### Q6 — Fórmula de monto total del profesional
**Elegido: A** — `monto_total = monto_cargas + monto_ajustes + suma_subtotales_bonos`.

### Q7 — Exportaciones XLS
**Elegido: A** — **XLS con bonos**: cantidad + subtotal por opción; **XLS agregado**: `monto_total` incluye bonos valorizados.

### Q8 — Roles ABM Producción
**Elegido: A** — Solo `admin` / `rrhh` (igual que Servicios, Módulos, Feriados).

### Q9 — Alta de tarifa: origen de los 4 campos
**Elegido: B** — Selector desde opciones ya detectadas en imports (`novedades_bono_opcion`); el usuario ingresa solo `valor_unitario`.

### Q10 — Tipo de `valor_unitario`
**Elegido: B** — Entero ≥ 0 (sin decimales). El valor 0 es tarifa válida.

### Q11 — Aviso de opciones sin tarifa
**Elegido: A** — Banner en Capital Humano cuando existan opciones del snapshot del período sin tarifa cargada.

### Q12 — Patrón UI del ABM
**Elegido: A** — Igual que Servicios: grilla + **Nueva producción** + editar/eliminar en modales + confirmación al borrar + Escape cancela.

## Resumen

| Tema | Decisión |
|------|----------|
| Ubicación | Tab **Producción** en Param (entre Módulos y Jefes ↔ servicios) |
| Match | Exacto `centro \| servicio \| semana \| horario` |
| Unicidad | Una tarifa por opción; editar para cambiar valor |
| Campos | 4 match + `valor_unitario` entero ≥ 0 |
| Alta | Selector de `novedades_bono_opcion` + valor |
| CH grilla | Cantidad + subtotal por opción |
| Sin tarifa | Cantidad sí; subtotal 0; banner CH |
| Total | cargas + ajustes + suma subtotales bonos |
| Export | XLS con bonos y agregado actualizados |
| Roles | admin / rrhh |

## Naming note

El tab **Producción** (tarifas de bonos) **no** es el checkbox **`produccion`** del módulo (skip check externo). Documentar en UI y runbook.
